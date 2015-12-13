import xml.sax
import time
import sys
import json
import multiprocessing
import requests

queue = multiprocessing.Queue(maxsize=8)
num_processes = 8
doc_count = 1
doc_limit = None
solr_url = 'http://localhost:8983/solr/localpedia'
clock = int(time.time())
doc_full_upload = 1122129 # grep -c '<doc>'

session = None

def send_doc(doc):
    res = session.post(solr_url + '/update', params={
        'wt': 'json',
        'commitWithin': 10000,
    }, headers={
        'Content-Type': 'application/json',
    }, data=json.dumps({'add': {'doc': doc}}))
    if not res.ok:
        print('Solr Error!')
        try:
            print(res.json()['error']['msg'])
        except:
            print(res.text)

def receive_docs():
    global session
    session = requests.session()
    while True:
        data = queue.get()
        if data == 'STOP':
            return
        else:
            send_doc(data)

class NoMoreDocs(Exception):
    pass

processes = []
for i in range(num_processes):
    p = multiprocessing.Process(target=receive_docs)
    p.start()
    processes.append(p)

def handle_wiki_doc(doc):
    global doc_count
    doc_count += 1

    if doc['title'].startswith('Wikipedia: '):
        doc['title'] = doc['title'].replace('Wikipedia: ', '', 1)
    doc['id'] = doc['title']
    if '|' in doc['abstract']:
        del doc['abstract']

    # Show progress
    global clock
    current_time = int(time.time())
    if current_time != clock:
        clock = current_time
        print('%.5f%%' % (doc_count / doc_full_upload * 100))

    queue.put(doc)
    return

    if doc_limit and doc_count > doc_limit:
        raise NoMoreDocs()

class WikipediaHandler(xml.sax.ContentHandler):
    def __init__(self, *args, **kwargs):
        xml.sax.ContentHandler.__init__(self, *args, **kwargs)
        self.doc = None
        self.text_buffer = ''
        self.fields = {'title', 'url', 'abstract'}

    def startElement(self, name, attrs):
        self.text_buffer = ''
        if name == "doc":
            self.doc = {}
        elif name in self.fields:
            self.reading = name
            self.doc[name] = ''

    def characters(self, text):
        self.text_buffer += text

    def endElement(self, name):
        if name == "doc":
            handle_wiki_doc(self.doc)
        elif name == self.reading:
            self.doc[name] = self.text_buffer.strip()

parser = xml.sax.make_parser()
parser.setContentHandler(WikipediaHandler())
try:
    parser.parse(open(sys.argv[1],"r"))
except NoMoreDocs:
    pass
for i in range(num_processes):
    queue.put('STOP')

for p in processes:
    p.join()

print('Finished')

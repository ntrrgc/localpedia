Localpedia
==========

I gave a talk (in Spanish) about deploying a search engine built on Solr, an open source search platform based on Lucene.

In it I described how it is set up, how documents can structured for Solr, the mechanisms it provides to convert raw textual information in indexable word stems, how indexes are created, how documents are feeded to the system and how search is performed.

As a demonstration application I create *Localpedia*: I download a dump of all the abstracts of Spanish wikipedia -- they are publicly available on [dumps.wikimedia.org](https://dumps.wikimedia.org/), parse them with Python and feed them to Solr. Then I build simple Flask web application that serves as frontend, allowing the user to look for articles.

This repository contains:

 * A document explaining Solr basics.

 * The source of Localpedia.

 * The configuration files used to set up Solr to index Localpedia.

Parallel Corpora 2
==================

Script consists of 2 parts:

  * article parser
  * aligner

Required software (install before using script):
  
  * yalign
  * additional Ubuntu packages:
    * mongodb
    * ipython
    * python-nose
    * python-werkzeug

Wiki article parser
-------------------

Article parser works in 2 steps:

  1. Extracts articles from wiki dumps
  2. Saves extracted articles to local DB (Mongo DB)

Before using parser, wiki dumps should be downloaded and extracted to some
directory (directory should contain *.xml, *.sql files). For each language 2
dump files should be downloaded - articles and language link dumps, here is
examples:

PL:
  * http://dumps.wikimedia.org/plwiki/latest/plwiki-latest-pages-articles.xml.bz2
  * http://dumps.wikimedia.org/plwiki/latest/plwiki-latest-langlinks.sql.gz

EN:
  * http://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
  * http://dumps.wikimedia.org/enwiki/latest/enwiki-latest-langlinks.sql.gz

IMPORTANT NOTE: Engilsh dumps after extraction will require about 50 Gb of free
space. During parsing parser can require up to 8 Gb ram.

Article parser have option "main language" - its language for which articles
extracted from other languages only if it exist in main language. Eg. if main
language is PL, then article extractor first extracts all article for PL, then
article for other languages and only if such articles exists in PL translation.
This reduces space requirements.

For help use:

$ python parse_wiki_dumps.py -h

Example command:

$ python parse_wiki_dumps.py -d ~/temp/wikipedia_dump/ -l pl -v

Wikipedia aligner
-----------------

Aligner can be used when article extracted from dumps.

Aligner takes article pairs for given language pair, aligns text and saves
parallel corpara to 2 files. Option "-s" can be used to limit number of symbols
in file (by default size is 50000000 symbols, thats around 50-60Mb)

By default aligner tries to continue aligning where it was stopped, to force
aligning from begining need to use "--restart" key

For help use:

$ python align.py -h

Example command:

$ python align.py -o wikipedia -l en-pl -v

Euronews crawler
----------------

Crawler finds links to articles using euronews archive
http://euronews.com/2004/, and in parallel extracts and saves article texts to
DB.

For help use:

$ python parse_euronews.py -h

Example command:

$ python parse_euronews.py -l en,pl -v

Euronews aligner
----------------

Starting aligner for euronews articles:

$ python align.py -o euronews -l en-pl -v

Saving articles in plain text
-----------------------------

Script "save_plain_text.py" can be used to save all articles in plain text
format, it accepts path for saving articles, languages of articles to be saved,
and source of articles (euronews, wikipedia).

For help use:

$ python save_plain_text.py -h

Example command:

$ python save_plain_text.py -l en,pl -r [path] -o euronews

Yalign selection
----------------
This script tries random parameters for model of yalign in order to get best
parameters for aligning provided text samples.

Before using yalign_selection script need to prepare article samples using
prepare_random_sampling.py script.

Creating folder with article samples can be done with this command:

$ python prepare_random_sampling.py -o wikipedia -c 10 -l ru-en -v

-o wikipedia - source of articles can be wikipedia or euronews

-c 10 - number of articles to extract

-l ru-en - languages to extract

This script will create "article_samples" folder with articles files, then you
can create manually aligned files (you need align article of second language),
for this example you need to align "en" file, files named "_orig" - should be
left unmodified

Then manual aligning is ready you can run selection script here is example:

$ python yalign_selection.py --samples article_samples/ --lang1 ru --lang2 en --threshold 0.1536422609112349e-6 --threshold_step 0.0000001 --threshold_step_count 10 --penalty 0.014928930455303857 --penalty_step 0.0001 --penalty_step_count 1 -m ru-en

Here is what each parameter means:

--samples article_samples/ - path to article samples folder

--lang1 ru --lang2 en - languages to align (articles of second language should
be aligned manually, script will be using "??_orig" files, align them
automatically and will compare with manually aligned)

--threshold 0.1536422609112349e-6 - threshold value of model, selection will be
made around this value

--threshold_step 0.0000001 - step of changing value

--threshold_step_count 10 - number of steps to check below and above vaule, eg
if value 10, step 1, and count 2, script will check 8 9 10 11 12

same parameters for penalty

-m ru-en - path to yalign model

Also you can use (to tweak comparison of text lines in files):

--length and --similarity
--length - min diffirence in length in order to mark lines similar, 1 - same
length, 0.5 - at least half of length
--similarity - similarity of text in lines, 1 - exactly same, 0 - completely
different. For similarity check sentences compared as sequence of characters.

It has multiprocessing support already. Use -t option to set number of threads,
by default it sets number of threads equal to number of CPU.

for additional parameters you can use '-h' key.

Then yalign_selection.py script will finish work it will produce csv file, with
first column equal to threshold, second column equal to penalty, and third is
similarity for this parameters.

Align with HUNALING method
----------------

In order to use hunalign you need add "--hunalign" option in align.py script, here is example:

$ python align.py -l li-hu -r align_result -o wikipedia --hunalign

In my empirical study it provides better results when articles are translations of each other or simillar in leghth and content.

Align From fodler
----------------
For aligning already aligned texts using hunalign:

Command exmaple is:

$ python align_aligned_using_hunalign.py source/ target/


Final info
=====

Wołk, K., & Marasek, K. (2015, September). Tuned and GPU-accelerated parallel data mining from comparable corpora. In International Conference on Text, Speech, and Dialogue (pp. 32-40). Springer International Publishing.

http://arxiv.org/pdf/1509.08639

For more detailed usage instruction see howto.pdf.

For any questions: | Krzysztof Wolk | krzysztof@wolk.pl

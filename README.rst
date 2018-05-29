Deep-Deep: Adaptive Crawler
===========================

.. image:: https://travis-ci.org/TeamHG-Memex/deep-deep.svg?branch=master
   :target: http://travis-ci.org/TeamHG-Memex/deep-deep
   :alt: Build Status

.. image:: http://codecov.io/github/TeamHG-Memex/deep-deep/coverage.svg?branch=master
   :target: http://codecov.io/github/TeamHG-Memex/deep-deep?branch=master
   :alt: Code Coverage


Deep-Deep is a Scrapy-based crawler which uses Reinforcement Learning methods
to learn which links to follow.

It is called Deep-Deep, but it doesn't use Deep Learning, and it is not only
for Deep web. Weird.


Running
-------

In order to run the spider, you need some seed urls and a relevancy function
that will provide reward value for each crawled page. There are some scripts
in ``./scripts`` with common use-cases:

* ``crawl-forms.py`` learns to find password recovery forms (they are classified
  with Formasaurus). This is a good benchmark task, because the spider must learn
  to plan several steps ahead (they are often best reachable via login links).
* ``crawl-keywords.py`` starts a crawl where relevance function is determined
  by a keywords file (keywords starting with "-" are considered negative).
* ``crawl-relevant.py`` start a crawl where reward is given by a
  classifier that returns a score with ``.predict_proba`` method.

There is also an extraction spider
``deepdeep.spiders.extraction.ExtractionSpider`` that learns to extract unique
items from a single domain given an item extractor.

For keywords and relevancy crawlers, the following files will be created
in the result folder:

* ``items.jl.gz`` - depending on the value of the ``export_cdr`` argument,
  either items in CDR format will be exported (default),
  or spider stats, including learning statistics (pass ``-a export_cdr=0``)
* ``meta.json`` - arguments of the spider
* ``params.json`` - full spider parameters
* ``Q-*.joblib`` - Q-model snapshots
* ``queue-*.csv.gz`` - queue snapshots
* ``events.out.tfevents.*`` - a log in TensorBoard_ format. Install
  TensorFlow_ to view it with ``tensorboard --logdir <result folder parent>``
  command.


Using trained model
-------------------

You can use deep-deep to just run adaptive crawls, updating link model and
collecting crawled data at the same time. But in some cases it is more
efficient to first train a link model with deep-deep, and then use this model
in another crawler. Deep-deep uses a lot
of memory to store page and link features, and more CPU to update the link
model. So if the link model is general enough to freeze it, you can run
a more efficient crawl. Or you might want to just use deep-deep link model
in an existing project.

This is all possible with ``deepdeep.predictor.LinkClassifier``: just load
it from ``Q-*.joblib`` checkpoint and use ``.extract_urls_from_response``
or ``.extract_urls`` methods to get a list of urls with scores.
An example of using this classifier in a simple scrapy spider is given in
``examples/standalone.py``. Note that in order to use default scrapy
queue, a float link score is converted to an integer priority value.

Note that in some rare cases the model might fail to generalize from
the crawl it was trained on to the new crawl.


Model explanation
-----------------

It's possible to explain model weights and predictions using eli5_ library.
For that you'll need to crawl with model checkpointing enabled and
storing items in CDR format. Crawled items are used in order to invert the
hashing vectorizer features, and also for prediction explanation.

``./scripts/explain-model.py`` can save a model explanation to pickle, html,
or print it in the terminal. But it is hard to analyze because character
ngram features are used.

``./scripts/explain-predictions.py`` will produce an html file for each
crawled page, where explanations for all link scores will be shown.


Testing
-------

To run tests, execute the following command from the ``deep-deep`` folder::

    ./check.sh

It requires Python 3.5+, pytest_, `pytest-cov`_, `pytest-twisted`_ and `mypy`_.

Alternatively, run ``tox`` from ``deep-deep`` folder.


.. _eli5: http://eli5.readthedocs.io/
.. _pytest: http://pytest.org/latest/
.. _pytest-cov: https://pytest-cov.readthedocs.io/
.. _pytest-twisted: https://github.com/schmir/pytest-twisted
.. _mypy: http://mypy-lang.org/
.. _TensorBoard: https://www.tensorflow.org/how_tos/summaries_and_tensorboard/
.. _TensorFlow: https://www.tensorflow.org/

----

.. image:: https://hyperiongray.s3.amazonaws.com/define-hg.svg
	:target: https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=deep-deep
	:alt: define hyperiongray

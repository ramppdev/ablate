.. image:: https://ramppdev.github.io/ablate/_static/logo_banner.png
   :alt: ablate turns deep learning experiments into structured, human-readable reports.
   :align: center

ablate
======

|pypi| |python_versions| |license|

`ablate` turns deep learning experiments into structured, human-readable reports. It is built around five principles:

* **composability**: sources, queries, blocks, and exporters can be freely combined
* **immutability**: query operations never mutate runs in-place, enabling safe reuse and functional-style chaining
* **extensibility**: sources, blocks, and exporters are designed to be easily extended with custom implementations
* **readability**: reports are generated with humans in mind: shareable, inspectable, and format-agnostic
* **minimal friction**: no servers, no databases, no heavy integrations: just Python and your existing logs

Currently, `ablate` supports the following `sources <https://ramppdev.github.io/ablate/modules/sources.html>`_
and `exporters <https://ramppdev.github.io/ablate/modules/exporters.html>`_:

* sources:
  `autrainer <https://github.com/autrainer/autrainer>`_,
  `ClearML <https://clear.ml/>`_,
  `MLflow <https://mlflow.org/>`_,
  `TensorBoard <https://www.tensorflow.org/tensorboard>`_,
  and `WandB <https://wandb.ai/>`_
* exporters: `Markdown <https://www.markdownguide.org/>`__ and `Jupyter <https://jupyter.org/>`_


.. |pypi| image:: https://img.shields.io/pypi/v/ablate?logo=pypi&logoColor=b4befe&color=b4befe
   :target: https://pypi.org/project/ablate/
   :alt: ablate PyPI Version

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/ablate?logo=python&logoColor=b4befe&color=b4befe
   :target: https://pypi.org/project/ablate/
   :alt: ablate Python Versions

.. |license| image:: https://img.shields.io/badge/license-MIT-b4befe?logo=c
   :target: https://github.com/ramppdev/ablate/blob/main/LICENSE
   :alt: ablate GitHub License


.. _installation:

Installation
------------

Install `ablate` using `pip`:

.. code:: bash

   pip install ablate

The following optional dependencies can be installed to enable additional features:

* ``ablate[clearml]`` to use `ClearML <https://clear.ml/>`_ as an experiment source
* ``ablate[mlflow]`` to use `MLflow <https://mlflow.org/>`_ as an experiment source
* ``ablate[tensorboard]`` to use `TensorBoard <https://www.tensorflow.org/tensorboard>`_ as an experiment source
* ``ablate[wandb]`` to use `WandB <https://wandb.ai/>`_ as an experiment source
* ``ablate[jupyter]`` to use `ablate` in a `Jupyter <https://jupyter.org/>`_ notebook


Quickstart
----------

`ablate` is built around five composable modules:

* `ablate.sources <https://ramppdev.github.io/ablate/modules/sources.html>`_: load experiment runs from various sources
* `ablate.queries <https://ramppdev.github.io/ablate/modules/queries.html>`_: apply queries and transformations to the runs
* `ablate.blocks <https://ramppdev.github.io/ablate/modules/blocks.html>`_: structure content as tables, text, figures, and other blocks
* `ablate.Report <https://ramppdev.github.io/ablate/modules/report.html>`_: create a report from the runs and blocks
* `ablate.exporters <https://ramppdev.github.io/ablate/modules/exporters.html>`_: export a report to various formats


Creating a Report
~~~~~~~~~~~~~~~~~

To create your first `Report <https://ramppdev.github.io/ablate/modules/reports.html#ablate.Report>`_, define one or more experiment sources.
For example, the built in `Mock <https://ramppdev.github.io/ablate/modules/sources.html#ablate.sources.Mock>`_ can be used to simulate runs:

.. code:: python

   from ablate.sources import Mock

   source = Mock(
       grid={"model": ["vgg", "resnet"], "lr": [0.01, 0.001]},
       num_seeds=2,
   )

Each run in the mock source has `accuracy`, `f1`, and `loss` metrics, along with a `seed` parameter
as well as the manually defined parameters `model` and `lr`.
Next, the runs can be loaded and processed using functional-style queries to e.g., sort by accuracy,
group by seed, aggregate the results by mean, and finally collect all results into a single list:

.. code:: python

   from ablate.queries import Metric, Param, Query

   runs = (
       Query(source.load())
       .sort(Metric("accuracy", direction="max"))
       .groupdiff(Param("seed"))
       .aggregate("mean")
       .all()
   )

Now that the runs are loaded and processed, a `Report <https://ramppdev.github.io/ablate/modules/reports.html#ablate.Report>`_
comprising multiple blocks can be created to structure the content:

.. code:: python

   from ablate import Report
   from ablate.blocks import H1, Table

   report = Report(runs)
   report.add(H1("Model Performance"))
   report.add(
       Table(
           columns=[
               Param("model", label="Model"),
               Param("lr", label="Learning Rate"),
               Metric("accuracy", direction="max", label="Accuracy"),
               Metric("f1", direction="max", label="F1 Score"),
               Metric("loss", direction="min", label="Loss"),
           ]
       )
   )

Finally, the report can be exported to a desired format such as
`Markdown <https://ramppdev.github.io/ablate/modules/exporters.html#ablate.exporters.Markdown>`_:

.. code:: python

   from ablate.exporters import Markdown

   Markdown().export(report)

This will produce a ``report.md`` file with the following content:

.. code:: markdown

   # Model Performance

   | Model   |   Learning Rate |   Accuracy |   F1 Score |    Loss |
   |:--------|----------------:|-----------:|-----------:|--------:|
   | resnet  |           0.01  |    0.94285 |    0.90655 | 0.0847  |
   | vgg     |           0.01  |    0.92435 |    0.8813  | 0.0895  |
   | resnet  |           0.001 |    0.9262  |    0.8849  | 0.0743  |
   | vgg     |           0.001 |    0.92745 |    0.90875 | 0.08115 |


Combining Sources
~~~~~~~~~~~~~~~~~

To compose multiple sources, they can be added together using the ``+`` operator as they represent lists of
`Run <https://ramppdev.github.io/ablate/modules/core.html#ablate.core.types.Run>`_ objects:

.. code:: python

   runs1 = Mock(...).load()
   runs2 = Mock(...).load()

   all_runs = runs1 + runs2 # combines both sources into a single list of runs


Selector Expressions
~~~~~~~~~~~~~~~~~~~~

`ablate` selectors are lightweight expressions that access attributes of experiment runs, such as parameters, metrics, or IDs.
They support standard Python comparison operators and can be composed using logical operators to define complex query logic:

.. code:: python

   accuracy = Metric("accuracy", direction="max")
   loss = Metric("loss", direction="min")

   runs = (
       Query(source.load())
       .filter((accuracy > 0.9) & (loss < 0.1))
       .all()
   )


Selectors return callable predicates, so they can be used in any query operation that requires a condition.
All standard comparisons are supported: ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``.
Logical operators ``&`` (and), ``|`` (or), and ``~`` (not) can be used to combine expressions:

.. code:: python

   from ablate.queries import Id

   select = (Param("model") == "resnet") | (Param("lr") < 0.001) # select resnet or LR below 0.001

   exclude = ~(Id() == "run-42") # exclude a specific run by ID

   runs = Query(source.load()).filter(select & exclude).all()


Functional Queries
~~~~~~~~~~~~~~~~~~

`ablate` queries are functionally pure such that intermediate results are not modified and can be reused:

.. code:: python

   runs = Mock(...).load()

   sorted_runs = Query(runs).sort(Metric("accuracy", direction="max"))

   filtered_runs = sorted_runs.filter(Metric("accuracy", direction="max") > 0.9)

   sorted_runs.all() # still contains all runs sorted by accuracy
   filtered_runs.all() # only contains runs with accuracy > 0.9
   

Composing Reports
~~~~~~~~~~~~~~~~~

By default, `ablate` reports populate blocks based on the global list of runs passed to the report during initialization.
To create more complex reports, blocks can be populated with a custom list of runs using the `runs` parameter:

.. code:: python

   report = Report(sorted_runs.all())
   report.add(H1("Report with Sorted Runs and Filtered Runs"))
   report.add(H2("Sorted Runs"))
   report.add(
       Table(
           columns=[
               Param("model", label="Model"),
               Param("lr", label="Learning Rate"),
               Metric("accuracy", direction="max", label="Accuracy"),
           ]
       )
   )
   report.add(H2("Filtered Runs"))
   report.add(
       Table(
           runs = filtered_runs.all(), # use filtered runs only for this block
           columns=[
               Param("model", label="Model"),
               Param("lr", label="Learning Rate"),
               Metric("accuracy", direction="max", label="Accuracy"),
           ]
       )
   )


Extending `ablate`
------------------

`ablate` is designed to be extensible, allowing you to create custom `sources <https://ramppdev.github.io/ablate/modules/sources.html>`_,
`blocks <https://ramppdev.github.io/ablate/modules/blocks.html>`_,
and `exporters <https://ramppdev.github.io/ablate/modules/exporters.html>`_ by implementing their respective abstract classes.

To contribute to `ablate`, please refer to the `contribution guide <https://ramppdev.github.io/ablate/development/contributing.html>`_.
.. image:: _static/logo_banner.png
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

Currently, `ablate` supports the following :ref:`sources <sources>` and :ref:`exporters <exporters>`:

* sources:
  `autrainer <https://github.com/autrainer/autrainer>`_,
  `ClearML <https://clear.ml/>`_,
  `MLflow <https://mlflow.org/>`_,
  `TensorBoard <https://www.tensorflow.org/tensorboard>`_,
  and `WandB <https://wandb.ai/>`_
* exporters: `Markdown <https://www.markdownguide.org/>`_ and `Jupyter <https://jupyter.org/>`_


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

.. code-block:: bash

   pip install ablate

The following optional dependencies can be installed to enable additional features:

* :attr:`ablate[clearml]` to use `ClearML <https://clear.ml/>`_ as an experiment source
* :attr:`ablate[mlflow]` to use `MLflow <https://mlflow.org/>`_ as an experiment source
* :attr:`ablate[tensorboard]` to use `TensorBoard <https://www.tensorflow.org/tensorboard>`_ as an experiment source
* :attr:`ablate[wandb]` to use `WandB <https://wandb.ai/>`_ as an experiment source
* :attr:`ablate[jupyter]` to use `ablate` in a `Jupyter <https://jupyter.org/>`_ notebook


Quickstart
----------

`ablate` is built around five composable modules:

* :ref:`ablate.sources <sources>`: load experiment runs from various sources
* :ref:`ablate.queries <queries>`: apply queries and transformations to the runs
* :ref:`ablate.blocks <blocks>`: structure content as tables, text, figures, and other blocks
* :ref:`ablate.Report <reports>`: create a report from the runs and blocks
* :ref:`ablate.exporters <exporters>`: export a report to various formats


Creating a Report
~~~~~~~~~~~~~~~~~

To create your first :class:`~ablate.Report`, define one or more experiment sources.
For example, the built in :class:`~ablate.sources.Mock` can be used to simulate runs:

.. code-block:: python
   :linenos:

   import ablate

   source = ablate.sources.Mock(
       grid={"model": ["vgg", "resnet"], "lr": [0.01, 0.001]},
       num_seeds=2,
   )

Each run in the mock source has `accuracy`, `f1`, and `loss` metrics, along with a `seed` parameter
as well as the manually defined parameters `model` and `lr`.
Next, the runs can be loaded and processed using functional-style queries to e.g., sort by accuracy,
group by seed, aggregate the results by mean, and finally collect all results into a single list:

.. code-block:: python
   :linenos:

   runs = (
       ablate.queries.Query(source.load())
       .sort(ablate.queries.Metric("accuracy", direction="max"))
       .groupdiff(ablate.queries.Param("seed"))
       .aggregate("mean")
       .all()
   )

Now that the runs are loaded and processed, a :class:`~ablate.Report` comprising multiple blocks 
can be created to structure the content:

.. code-block:: python
   :linenos:

   report = ablate.Report(runs)
   report.add(ablate.blocks.H1("Model Performance"))
   report.add(
       ablate.blocks.Table(
           columns=[
               ablate.queries.Param("model", label="Model"),
               ablate.queries.Param("lr", label="Learning Rate"),
               ablate.queries.Metric("accuracy", direction="max", label="Accuracy"),
               ablate.queries.Metric("f1", direction="max", label="F1 Score"),
               ablate.queries.Metric("loss", direction="min", label="Loss"),
           ]
       )
   )

Finally, the report can be exported to a desired format such as :class:`~ablate.exporters.Markdown`:

.. code-block:: python
   :linenos:

   ablate.exporters.Markdown().export(report)

This will produce a :file:`report.md` file with the following content:

.. code-block:: markdown

   # Model Performance

   | Model   |   Learning Rate |   Accuracy |   F1 Score |    Loss |
   |:--------|----------------:|-----------:|-----------:|--------:|
   | resnet  |           0.01  |    0.94285 |    0.90655 | 0.0847  |
   | vgg     |           0.01  |    0.92435 |    0.8813  | 0.0895  |
   | resnet  |           0.001 |    0.9262  |    0.8849  | 0.0743  |
   | vgg     |           0.001 |    0.92745 |    0.90875 | 0.08115 |


Combining Sources
~~~~~~~~~~~~~~~~~

To compose multiple sources, they can be added together using the :attr:`+` operator
as they represent lists of :class:`~ablate.core.types.Run` objects:

.. code-block:: python
   :linenos:

   runs1 = ablate.sources.Mock(...).load()
   runs2 = ablate.sources.Mock(...).load()

   all_runs = runs1 + runs2 # combines both sources into a single list of runs


Functional Queries
~~~~~~~~~~~~~~~~~~

`ablate` queries are functionally pure such that intermediate results are not modified and can be reused:

.. code-block:: python
   :linenos:

   runs = ablate.sources.Mock(...).load()

   sorted_runs = Query(runs).sort(ablate.queries.Metric("accuracy", direction="max"))

   filtered_runs = sorted_runs.filter(
       ablate.queries.Metric("accuracy", direction="max") > 0.9
   )

   sorted_runs.all() # still contains all runs sorted by accuracy
   filtered_runs.all() # only contains runs with accuracy > 0.9
   

Composing Reports
~~~~~~~~~~~~~~~~~

By default, `ablate` reports populate blocks based on the global list of runs passed to the report during initialization.
To create more complex reports, blocks can be populated with a custom list of runs using the `runs` parameter:

.. code-block:: python
   :linenos:

   report = ablate.Report(sorted_runs.all())
   report.add(ablate.blocks.H1("Report with Sorted Runs and Filtered Runs"))
   report.add(ablate.blocks.H2("Sorted Runs"))
   report.add(
       ablate.blocks.Table(
           columns=[
               ablate.queries.Param("model", label="Model"),
               ablate.queries.Param("lr", label="Learning Rate"),
               ablate.queries.Metric("accuracy", direction="max", label="Accuracy"),
           ]
       )
   )
   report.add(ablate.blocks.H2("Filtered Runs"))
   report.add(
       ablate.blocks.Table(
           runs = filtered_runs.all(), # use filtered runs only for this block
           columns=[
               ablate.queries.Param("model", label="Model"),
               ablate.queries.Param("lr", label="Learning Rate"),
               ablate.queries.Metric("accuracy", direction="max", label="Accuracy"),
           ]
       )
   )

Extending `ablate`
------------------

`ablate` is designed to be extensible, allowing you to create custom :ref:`sources <sources>`, :ref:`blocks <blocks>`,
and :ref:`exporters <exporters>` by implementing their respective abstract classes.

To contribute to `ablate`, please refer to the :ref:`contribution guide <contributing>`.
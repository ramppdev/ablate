.. _sources:

Sources
=======

Sources are responsible for loading experiment runs from various deep learning experiment tracking tools or logs.
Each source loads a list of :class:`~ablate.core.types.Run` objects containing parameters, metrics, and optional temporal data
using the :meth:`~ablate.sources.AbstractSource.load` method.

Loaded runs be combined using the :attr:`+` operator to merge multiple sources into a single list of runs.

.. tip::

   To create custom sources, inherit from :class:`~ablate.sources.AbstractSource`
   and implement the :meth:`~ablate.sources.AbstractSource.load` method.


Abstract Source
---------------

.. autoclass:: ablate.sources.AbstractSource
   :members:


Experiment Sources
------------------

.. autoclass:: ablate.sources.Autrainer
   :members:

.. autoclass:: ablate.sources.ClearML
   :members:

.. autoclass:: ablate.sources.MLflow
   :members:

.. autoclass:: ablate.sources.TensorBoard
   :members:

.. autoclass:: ablate.sources.WandB
   :members:


Mock Source
-----------

.. autoclass:: ablate.sources.Mock
   :members:
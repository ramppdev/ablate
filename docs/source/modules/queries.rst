.. _queries:

Queries
=======

Queries are used to transform, filter, and organize experiment runs in a functional and composable way.
They operate on lists of :class:`~ablate.core.types.Run` objects and return new a (grouped) query, preserving immutability.

Typical operations include filtering, sorting, grouping, aggregating, and computing derived values.
All queries are applied through the :class:`~ablate.queries.Query` and :class:`~ablate.queries.GroupedQuery` interfaces using a chainable syntax.

.. tip::
   
   Queries can be reused and recombined without modifying the original data.


Query and Grouped Query
-----------------------

.. autoclass:: ablate.queries.Query
   :members:

.. autoclass:: ablate.queries.GroupedQuery
   :members:


Query Selectors
---------------

Query selectors are the building blocks for expressing transformations.
Selectors can be used directly in queries to define filter conditions, sort keys, group keys, and aggregations.

.. autoclass:: ablate.queries.AbstractSelector
   :members:


Parameter Selectors
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ablate.queries.AbstractParam
   :members:

.. autoclass:: ablate.queries.Id
   :members:

.. autoclass:: ablate.queries.Param
   :members:


Metric Selectors
~~~~~~~~~~~~~~~~

.. autoclass:: ablate.queries.AbstractMetric
   :members:

.. autoclass:: ablate.queries.Metric
   :members:

.. autoclass:: ablate.queries.TemporalMetric
   :members:
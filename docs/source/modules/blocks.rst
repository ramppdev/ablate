.. _blocks:

Blocks
======

Blocks are modular content units used to structure a :class:`~ablate.Report`.
They define how runs are structured, however not how they are rendered or exported.

Each block operates on a list of :class:`~ablate.core.types.Run` objects, either globally (from the report) or locally via the runs argument.

.. tip::

   To create custom blocks, inherit from :class:`~ablate.blocks.AbstractBlock`
   and implement the :meth:`~ablate.blocks.AbstractBlock.build` method.


Abstract Block
--------------

.. autoclass:: ablate.blocks.AbstractBlock
   :members:


Text Blocks
-----------

.. autoclass:: ablate.blocks.AbstractTextBlock
   :members:

.. autoclass:: ablate.blocks.Text
   :members:

.. autoclass:: ablate.blocks.H1
   :members:

.. autoclass:: ablate.blocks.H2
   :members:

.. autoclass:: ablate.blocks.H3
   :members:

.. autoclass:: ablate.blocks.H4
   :members:

.. autoclass:: ablate.blocks.H5
   :members:

.. autoclass:: ablate.blocks.H6
   :members:


Table Blocks
------------

.. autoclass:: ablate.blocks.AbstractTableBlock
   :members:

.. autoclass:: ablate.blocks.Table
   :members:


Metric Blocks
-------------

.. autoclass:: ablate.blocks.AbstractFigureBlock
   :members:

.. autoclass:: ablate.blocks.MetricPlot
   :members:

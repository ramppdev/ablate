.. _reports:

Reports
=======

A :class:`~ablate.Report` defines and organizes the structure of experiment results.
It holds a list of :class:`~ablate.core.types.Run` objects and a sequence of content :ref:`blocks <blocks>`.

Reports are composed of individual blocks such as headings, tables, text sections, or figures.
These blocks define the structure of the report, while :ref:`exporters <exporters>` define how the report is rendered and saved.

.. tip::
   By default, all blocks in a report use the global list of runs unless a
   :ref:`block <blocks>` is initialized with a specific list of runs via its :attr:`runs` attribute.


Report
------

.. autoclass:: ablate.Report
   :members:

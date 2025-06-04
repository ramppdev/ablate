.. _exporters:

Exporters
=========

Exporters are responsible for converting a :class:`~ablate.Report` into a target format such as :class:`~ablate.exporters.Markdown`.

Multiple exporters can be used interchangeably to render the same report in different formats.

.. tip::

   To create custom exporters, inherit from :class:`~ablate.exporters.AbstractExporter` and implement the
   :meth:`~ablate.exporters.AbstractExporter.render_text`, :meth:`~ablate.exporters.AbstractExporter.render_table`,
   :meth:`~ablate.exporters.AbstractExporter.render_figure`, and :meth:`~ablate.exporters.AbstractExporter.export` methods.


Abstract Exporter
-----------------

.. autoclass:: ablate.exporters.AbstractExporter
   :members:


Report Exporters
----------------

.. autoclass:: ablate.exporters.Markdown
   :members:

.. autoclass:: ablate.exporters.Notebook
   :members:

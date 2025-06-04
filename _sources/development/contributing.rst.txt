.. _contributing:

Contributing
============

Contributions are welcome!
If you would like to contribute to `ablate`, please open an issue or a pull request on the
`GitHub repository <https://github.com/ramppdev/ablate>`_.


Installation
------------

It is recommended to install `ablate` within a virtual environment for development.
To create a new virtual environment, refer to the `Python venv documentation <https://docs.python.org/3/library/venv.html>`_.

To set up `ablate` for development, start by cloning the repository and
then install the development dependencies using `uv <https://docs.astral.sh/uv/>`_:

.. code-block:: bash

   git clone git@github.com:ramppdev/ablate.git
   cd ablate
   uv sync --all-extras --all-groups


Conventions
-----------

We use `Ruff <https://docs.astral.sh/ruff/>`_ to enforce code style and formatting.
Common spelling errors are automatically corrected by `codespell <https://github.com/codespell-project/codespell>`_.
Type checking is performed using `mypy <https://mypy.readthedocs.io/en/stable/>`_.

Linting, formatting, and spelling checks are run with `pre-commit <https://pre-commit.com/>`_.
To install the pre-commit hooks, run the following command:

.. code-block:: bash

   pre-commit install

To locally run the pre-commit hooks, use:

.. code-block:: bash

   pre-commit run --all-files


Testing
-------

We use `pytest <https://docs.pytest.org/en/stable/>`_ for testing.
To run the tests, use the following command:

.. code-block:: bash

   pytest
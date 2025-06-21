<div align="center">
  <img src="https://ramppdev.github.io/ablate/_images/logo_banner.png" alt="ablate turns deep learning experiments into structured, human-readable reports.">
</div>

# ablate

[![ablate PyPI Version](https://img.shields.io/pypi/v/ablate?logo=pypi&logoColor=b4befe&color=b4befe)](https://pypi.org/project/ablate/)
[![ablate Python Versions](https://img.shields.io/pypi/pyversions/ablate?logo=python&logoColor=b4befe&color=b4befe)](https://pypi.org/project/ablate/)
[![ablate GitHub License](https://img.shields.io/badge/license-MIT-b4befe?logo=c)](https://github.com/ramppdev/ablate/blob/main/LICENSE)

_ablate_ turns deep learning experiments into structured, human-readable reports. It is built around five principles:

- **composability**: sources, queries, blocks, and exporters can be freely combined
- **immutability**: query operations never mutate runs in-place, enabling safe reuse and functional-style chaining
- **extensibility**: sources, blocks, and exporters are designed to be easily extended with custom implementations
- **readability**: reports are generated with humans in mind: shareable, inspectable, and format-agnostic
- **minimal friction**: no servers, no databases, no heavy integrations: just Python and your existing logs

Currently, _ablate_ supports the following [sources](https://ramppdev.github.io/ablate/modules/sources.html)
and [exporters](https://ramppdev.github.io/ablate/modules/exporters.html):

- sources:
  [autrainer](https://github.com/autrainer/autrainer),
  [ClearML](https://clear.ml/),
  [MLflow](https://mlflow.org/),
  [TensorBoard](https://www.tensorflow.org/tensorboard),
  and [WandB](https://www.wandb.ai/)
- exporters: [Markdown](https://www.markdownguide.org) and [Jupyter](https://jupyter.org/)

## Installation

Install _ablate_ using _pip_:

```bash
pip install ablate
```

The following optional dependencies can be installed to enable additional features:

- `ablate[clearml]` to use [ClearML](https://clear.ml/) as an experiment source
- `ablate[mlflow]` to use [MLflow](https://mlflow.org/) as an experiment source
- `ablate[tensorboard]` to use [TensorBoard](https://www.tensorflow.org/tensorboard) as an experiment source
- `ablate[wandb]` to use [WandB](https://www.wandb.ai/) as an experiment source
- `ablate[jupyter]` to use _ablate_ in a [Jupyter](https://jupyter.org/) notebook

## Quickstart

_ablate_ is built around five composable modules:

- [ablate.sources](https://ramppdev.github.io/ablate/modules/sources.html): load experiment runs from various sources
- [ablate.queries](https://ramppdev.github.io/ablate/modules/queries.html): apply queries and transformations to the runs
- [ablate.blocks](https://ramppdev.github.io/ablate/modules/blocks.html): structure content as tables, text, figures, and other blocks
- [ablate.Report](https://ramppdev.github.io/ablate/modules/report.html): create a report from the runs and blocks
- [ablate.exporters](https://ramppdev.github.io/ablate/modules/exporters.html): export a report to various formats

### Creating a Report

To create your first [Report](https://ramppdev.github.io/ablate/modules/report.html), define one or more experiment sources.
For example, the built in [Mock](https://ramppdev.github.io/ablate/modules/sources.html#mock-source) can be used to simulate runs:

```python
from ablate.sources import Mock

source = Mock(
  grid={"model": ["vgg", "resnet"], "lr": [0.01, 0.001]},
  num_seeds=2,
)
```

Each run in the mock source has _accuracy_, _f1_, and _loss_ metrics, along with a _seed_ parameter
as well as the manually defined parameters _model_ and _lr_.
Next, the runs can be loaded and processed using functional-style queries to e.g., sort by accuracy,
group by seed, aggregate the results by mean, and finally collect all results into a single list:

```python
from ablate.queries import Query, Metric, Param

runs = (
    Query(source.load())
    .sort(Metric("accuracy", direction="max"))
    .groupdiff(Param("seed"))
    .aggregate("mean")
    .all()
)

```

Now that the runs are loaded and processed, a [Report](https://ramppdev.github.io/ablate/modules/report.html)
comprising multiple blocks can be created to structure the content:

```python
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
```

Finally, the report can be exported to a desired format such as [Markdown](https://ramppdev.github.io/ablate/modules/exporters.html#ablate.exporters.Markdown):

```python
from ablate.exporters import Markdown

Markdown().export(report)
```

This will produce a `report.md` file with the following content:

```markdown
# Model Performance

| Model  | Learning Rate | Accuracy | F1 Score |    Loss |
| :----- | ------------: | -------: | -------: | ------: |
| resnet |          0.01 |  0.94285 |  0.90655 |  0.0847 |
| vgg    |          0.01 |  0.92435 |   0.8813 |  0.0895 |
| resnet |         0.001 |   0.9262 |   0.8849 |  0.0743 |
| vgg    |         0.001 |  0.92745 |  0.90875 | 0.08115 |
```

### Combining Sources

To compose multiple sources, they can be added together using the `+` operator
as they represent lists of [Run](https://ramppdev.github.io/ablate/modules/core.html#ablate.core.types.Run) objects:

```python
runs1 = Mock(...).load()
runs2 = Mock(...).load()

all_runs = runs1 + runs2 # combines both sources into a single list of runs
```

### Selector Expressions

_ablate_ selectors are lightweight expressions that access attributes of experiment runs, such as parameters, metrics, or IDs.
They support standard Python comparison operators and can be composed using logical operators to define complex query logic:

```python
accuracy = Metric("accuracy", direction="max")
loss = Metric("loss", direction="min")

runs = (
    Query(source.load())
    .filter((accuracy > 0.9) & (loss < 0.1))
    .all()
)
```

Selectors return callable predicates, so they can be used in any query operation that requires a condition.
All standard comparisons are supported: `==`, `!=`, `<`, `<=`, `>`, `>=`.
Logical operators `&` (and), `|` (or), and `~` (not) can be used to combine expressions:

```python
from ablate.queries import Id

select = (Param("model") == "resnet") | (Param("lr") < 0.001) # select resnet or LR below 0.001

exclude = ~(Id() == "run-42") # exclude a specific run by ID

runs = Query(source.load()).filter(select & exclude).all()

```

### Functional Queries

_ablate_ queries are functionally pure such that intermediate results are not modified and can be reused:

```python
runs = Mock(...).load()

sorted_runs = Query(runs).sort(Metric("accuracy", direction="max"))

filtered_runs = sorted_runs.filter(Metric("accuracy", direction="max") > 0.9)

sorted_runs.all() # still contains all runs sorted by accuracy
filtered_runs.all() # only contains runs with accuracy > 0.9
```

### Composing Reports

By default, _ablate_ reports populate blocks based on the global list of runs passed to the report during initialization.
To create more complex reports, blocks can be populated with a custom list of runs using the _runs_ parameter:

```python
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
```

## Extending _ablate_

_ablate_ is designed to be extensible, allowing you to create custom [sources](https://ramppdev.github.io/ablate/modules/sources.html),
[blocks](https://ramppdev.github.io/ablate/modules/blocks.html),
and [exporters](https://ramppdev.github.io/ablate/modules/exporters.html) by implementing their respective abstract classes.

To contribute to _ablate_, please refer to the [contribution guide](https://ramppdev.github.io/ablate/development/contributing.html).

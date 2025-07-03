# clp-s methodology

## Basics

Version: [0.2.0][download]

## Setup

First, download the latest released binary, or clone the latest [code][clp] and compile it locally
by following these [instructions][core-build]. Then we use `clp-s` binary.

## Specifics

The setup for CLP-S is almost the same as that of CLP. The only difference is the query format: JSON
log queries use [kql], as specified in the `queries` field of `config.yaml`.


[clp]: https://github.com/y-scope/clp
[core-build]: https://docs.yscope.com/clp/main/dev-guide/components-core/index.html
[download]: https://github.com/y-scope/clp/releases/tag/v0.2.0
[kql]: https://docs.yscope.com/clp/main/user-guide/reference-json-search-syntax.html

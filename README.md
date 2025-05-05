## nuanced

nuanced uses static analysis to generate enriched function call graphs of Python packages, providing agents and coding assistants with deeper understanding of code behavior.

Docs: https://docs.nuanced.dev

### CLI Quick Start

**Install nuanced**

```bash
uv tool install nuanced
```

**Initialize a graph**

```bash
cd my_project
nuanced init path/to/my_package
```

**Enrich and add context**

```bash
nuanced enrich path/to/my_package/file.py some_function_name > some_function_name_subgraph.json
```

```bash
echo "test_some_function_name_succeeds is failing. Can you use the call graph in
some_function_name_subgraph.json to debug and update the relevant code to make
the test pass?" > agent_prompt.txt
```

### Contributing

#### Setup

1. Set up and activate virtualenv

```bash
% cd nuanced
% uv venv
% source .venv/bin/activate
```

2. Install dependencies

```bash
% uv sync
```

#### Running tests

```bash
% pytest
```

#### Releasing new versions

https://docs.nuanced.dev/versioning#release-process

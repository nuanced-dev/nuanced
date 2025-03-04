## nuanced

nuanced uses static analysis to generate enriched function call graphs of Python modules, providing agents and coding assistants with deeper understanding of code behavior.

Docs: https://docs.nuanced.dev

### CLI Quick Start

**Install nuanced**

```bash
uv tool install nuanced
```

**Initialize the graph**

```bash
cd my_project
nuanced init my_python_module
```

**Enrich and add context**

```bash
nuanced enrich path/to/module/file.py some_function_name > some_function_name_subgraph.json
```

```bash
echo "test_some_function_name_succeeds is failing. Can you use the call graph in
some_function_name_subgraph.json to debug and update the relevant code to make
the test pass?" > agent_prompt.txt
```

### Contributing

#### Setup

1. Clone the repo

```bash
% git clone git@github.com:nuanced-dev/nuanced.git
```

2. Set up and activate virtualenv

```bash
% cd nuanced-graph
% uv venv
% source .venv/bin/activate
```

3. Install dependencies

```bash
% uv sync
```

#### Running tests

```bash
% pytest
```

## Luma API Python client

**WARNING:** We are no longer actively supporting this capture API. For Genie API, please contact us for information.

### Installation

`pip install lumaapi`

### Docs

[https://lumalabs.ai/luma-api/client-docs/index.html](https://lumalabs.ai/luma-api/client-docs/index.html)

To build docs: go to docs/ and
```sh
make html
```

Need to install requirements first time (`pip install -r docs/requirements.txt`)


###  Release
First install deps `pip install python-build twine`

Then update the version in `pyproject.toml` and
```sh
python -m build
twine upload dist/lumaapi-<x.x.x>.tar.gz
```

For Luma employees: Please get the password from 1Password (search PyPI)


### CLI usage

- To submit a video: `luma submit <path> <title>`,
  where path can be a video, zip, or directory.
  - This outputs a slug.
- To check status of the capture: `luma status <slug>`
- To search user's captures: `luma get <title>`
- To manually authenticate: `luma auth` (CLI will also prompt when required)
- To check for credits: `luma credits`

### Library usage
```python
from lumaapi import LumaClient
client = LumaClient(api_key)
slug = client.submit(video_path, title)
print(client.status(slug))
```

Then use functions corresponding to the CLI


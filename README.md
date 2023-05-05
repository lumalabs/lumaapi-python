## Luma API Python client

### Installation

`pip install lumaapi`

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

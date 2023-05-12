Luma API Python + CLI Client Reference
=========================================================

This is a Python and CLI client for the `Luma API <https://lumalabs.ai/luma-api>`_.
Both are included in the pure-Python library :code:`lumaapi`, which you can install from PyPI:

.. code-block:: shell

    pip install lumaapi

We assume you already have Python 3 with pip installed.


Example CLI usage
*****************************

.. code-block:: shell

    # Check credits
    luma credits
    # Submit video, zip, or folder (of images). Prints slug
    luma submit <path> <title>
    # Check status of slug
    luma status <slug>

If not already logged in, you will be prompted
for an API key. You may obtain
one from the `Luma API dashboard <https://captures.lumalabs.ai/dashboard>`_.
You may also manually authenticate with

.. code-block:: shell

    luma auth <api-key>


Example usage inside Python
*****************************

.. code-block:: python

    from lumaapi import LumaClient
    client = LumaClient(api_key)
    slug = client.submit(video_path, title)
    print(client.status(slug))

Again, you may obtain an API key from the `Luma API dashboard <https://captures.lumalabs.ai/dashboard>`_.
Any of the functions in LumaClient may be used directly in the CLI e.g.

.. code-block:: shell

    client.submit(video_path, title)
    luma submit video_path title

Please see detailed per-function documentation below.


LumaClient
*****************************

.. autoclass:: lumaapi.LumaClient
   :members:


Misc Types
*****************************

.. autoclass:: lumaapi.LumaCreditInfo
   :members:

.. autoclass:: lumaapi.LumaCaptureInfo
   :members:

.. autoclass:: lumaapi.LumaRunInfo
   :members:

.. autoenum:: lumaapi.PrivacyLevel
   :members:

.. autoenum:: lumaapi.CaptureStatus
   :members:

.. autoenum:: lumaapi.RunStatus
   :members:

.. autoenum:: lumaapi.CaptureType
   :members:

.. autoenum:: lumaapi.CameraType
   :members:

.. autoclass:: lumaapi.CaptureLocation
   :members:

Note:
This doc uses `Ruilong Li's fork of the PyTorch Sphinx theme <https://github.com/liruilong940607/pytorch_sphinx_theme>`_
used for `nerfacc <https://www.nerfacc.com>`_

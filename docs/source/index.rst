.. _lumaapi:

Luma API Python + CLI Client Reference
=========================================================

This is a Python and CLI client for the `Luma API <https://lumalabs.ai/luma-api>`_
Both are included in the pure-Python library :code:`lumaapi`.

* Installation: you can install it from PyPI

.. code-block:: shell

    pip install lumaapi


* Luma API: `Dashboard <https://captures.lumalabs.ai/dashboard>`_,
  `API reference <https://documenter.getpostman.com/view/24305418/2s93CRMCas>`_

Example CLI usage
*****************************

.. code-block:: shell

    # Check credits
    luma credits
    # Submit video, zip, or folder (of images). Prints slug
    luma submit <path> <title>
    # Check status of slug
    luma status <slug>


Example usage inside Python
*****************************

.. code-block:: python

    from lumaapi import LumaClient
    client = LumaClient(api_key)
    slug = client.submit(video_path, title)
    print(client.status(slug))

Any of the functions in LumaClient may be used directly in the CLI e.g.
:code:`luma submit video_path title`


Reference: LumaClient
*****************************

.. autoclass:: lumaapi.LumaClient
   :members:


Reference: Misc Types
*****************************

.. autoclass:: lumaapi.LumaCreditInfo
   :members:

.. autoclass:: lumaapi.LumaCaptureInfo
   :members:

.. autoclass:: lumaapi.PrivacyLevel
   :members:
   :show-inheritance:

.. autoclass:: lumaapi.CaptureLocation
   :members:

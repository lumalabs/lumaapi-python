.. _lumaapi:

Reference
============

Example usage inside python

.. code-block:: python

    from lumaapi import LumaClient
    client = LumaClient(api_key)
    slug = client.submit(video_path, title)
    print(client.status(slug))

Any of the functions in LumaClient may be used directly in the CLI e.g.
:code:`luma submit video_path title`


.. autoclass:: lumaapi.LumaClient
   :members:

.. autoclass:: lumaapi.LumaCreditInfo
   :members:

.. autoclass:: lumaapi.LumaCaptureInfo
   :members:
   
.. autoclass:: lumaapi.PrivacyLevel
   :members:
   :show-inheritance:

.. autoclass:: lumaapi.CaptureLocation
   :members:

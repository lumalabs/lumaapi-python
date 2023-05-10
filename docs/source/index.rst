.. lumaapi documentation master file, created by
   sphinx-quickstart on Wed Sep 15 10:48:24 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Luma API Python + CLI Client Reference
=========================================================

This is a Python and CLI client for the `Luma API <https://lumalabs.ai/luma-api>`_

* Installation: :code:`pip install lumaapi`
* Python library reference: :ref:`lumaapi`
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


Please see the reference for more details

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   lumaapi

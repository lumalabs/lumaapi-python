# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import subprocess
import pytorch_sphinx_theme
sys.path.insert(0, os.path.join(os.path.abspath('.'), '..'))


# -- Project information -----------------------------------------------------

project = 'lumaapi'
copyright = '2023, Luma AI'
author = 'Luma AI'

# The full version, including alpha/beta/rc tags

release = subprocess.check_output(sys.executable + " -m pip show lumaapi | grep Version | cut -d ' ' -f 2",
                                  shell=True).decode('utf-8').strip()
print('lumaapi', release)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
        'recommonmark',
		'sphinx.ext.napoleon',
		'sphinx.ext.duration',
		'sphinx.ext.doctest',
		'sphinx.ext.autodoc',
		'sphinx.ext.autosummary',
		#  'sphinx.ext.intersphinx',
        'pytorch_sphinx_theme',
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pytorch_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_theme_path = [pytorch_sphinx_theme.get_html_theme_path()]
html_static_path = ["_static"]
html_css_files = ["css/readthedocs.css"]

copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True

add_module_names = False

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)

autodoc_member_order = 'bysource'

html_theme_options = {
    #  'collapse_navigation': False,
    #  'sticky_navigation': True,
    "logo_url": "/",
    "menu": [
        {"name": "API home",
         "url": "https://lumalabs.ai/luma-api"},
        {"name": "API dashboard",
         "url": "https://captures.lumalabs.ai/dashboard"},
        {"name": "API reference",
         "url": "https://documenter.getpostman.com/view/24305418/2s93CRMCas"},
	],
}

epub_show_urls = "footnote"

# typehints
autodoc_typehints = "description"

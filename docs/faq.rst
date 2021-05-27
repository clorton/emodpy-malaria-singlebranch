==========================
Frequently asked questions
==========================

As you get started with |EMODPY_s| and |EMODPY_malaria|, you may have questions.
The questions in :doc:`emodpy:faq` in the |EMODPY_s| documentation are common
to all packages that build on |EMODPY_s| and |emod_api|. The questions below
are specific to |EMODPY_malaria|. If any of the concepts or terms are unfamiliar,
consult the |EMOD_s| :doc:`emod-malaria:glossary`. 

.. contents:: Contents
   :local:


How do I set configuration parameters?
======================================

Define your own parameter-setting function such as ``set_param_fn`` and pass
that function to the |EMODPY_s| task creator as the ``param_custom_cb``
parameter. In that function, you can set the parameters directly. For
example:

.. literalinclude:: ..\examples\start_here\example.py
   :lines: 55-82

See examples/start_here/example.py. for additional information.

If you prefer something more modular, you can call a function in a standalone
script/file that sets the configuration parameters.

Are there defaults?
===================

Great question. If you don't set any configuration parameters, they will have
defaults based on the schema. The malaria team has set team defaults in 
:py:meth:`emodpy_malaria.config.set_team_defaults`. These defaults can be seen
in `config.py <../emodpy_malaria/config.py>`_. 


How do I specify the log level for |EMOD_s|? I get a schema error when I try to set it now.
===========================================================================================

TBD

How do I specify the vector species for my scenario?
====================================================

See the excerpt below or the complete example of setting the vector species
and parameter values associated with each species in
examples\\start_here\\example.py. 

.. literalinclude:: ..\examples\start_here\example.py
   :lines: 55-82

A helper function to make this task even easier may be coming shortly. 

I pip installed |EMODPY_malaria|, but I want to make changes. How should I do that?
===================================================================================

Install at a command prompt using the following::

	python package_setup.py develop

This method is the most popular and proven, though there are some other
options. Installing this way means that the |EMODPY_malaria| module in
site-packages actually points to the same code as you have checked out in git.
For more detail, see this `Stack Overflow post
<https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install#19048754>`_.

However, we aim to get the desired changes quickly tested and included in the
versioned module we release via pip install.

I see a lot of MALARIA_SIM examples. Are there any VECTOR_SIM examples?
=======================================================================

Yes! The following examples use VECTOR_SIM:

   * examples/migration_spatial_vector_sim
   * examples/vector_basic
   * examples/vector_genetics_insecticide_resistance
   * examples/vector_genetics_vector_sim

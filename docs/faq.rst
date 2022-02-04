==========================
Frequently asked questions
==========================

As you get started with |EMODPY_malaria|, you may have questions. The most common
questions are answered below. The most common questions are answered below. 
For questions related to functionality in related packages, see the
following documentation:

* :doc:`emod-malaria:faq` for |EMOD_s|
* :doc:`idmtools:faq` for |IT_s|
* :doc:`emod_api:faq` for |emod_api|
* :doc:`emodpy:faq` for |EMODPY_s|  


How do I set configuration parameters?
   Define your own parameter-setting function such as ``set_param_fn`` and pass
   that function to the |EMODPY_s| task creator as the ``param_custom_cb``
   parameter. In that function, you can set the parameters directly. For
   example:

   .. literalinclude:: ../examples/start_here/example.py
      :lines: 55-82

   See examples/start_here/example.py. for additional information.

   If you prefer something more modular, you can call a function in a standalone
   script/file that sets the configuration parameters.

Are there defaults?
   Great question. If you don't set any configuration parameters, they will have
   defaults based on the schema. The malaria team has set team defaults in
   :py:meth:`emodpy_malaria.config.set_team_defaults`. These defaults can be seen
   in `config.py <https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/emodpy_malaria/config.py>`_.


.. How do I specify the log level for |EMOD_s|? I get a schema error when I try to set it now.

.. TBD

How do I specify the vector species for my scenario?
   See the excerpt below or the complete example of setting the vector species
   and parameter values associated with each species in
   examples/start_here/example.py.

   .. literalinclude:: ../examples/start_here/example.py
      :lines: 55-82

   A helper function to make this task even easier may be coming shortly.

I pip installed |EMODPY_malaria|, but I want to make changes. How should I do that?
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
   Yes! The following examples use VECTOR_SIM:

      * examples/migration_spatial_vector_sim
      * examples/vector_basic
      * examples/vector_genetics_insecticide_resistance
      * examples/vector_genetics_vector_sim

Is there a multi-node or spatial example?
   Yes. See:

      * examples/migration_spatial_vector_sim
      * examples/migration_spatial_malaria_sim
      * examples/jonr_1

Are there simple campaign/intervention examples?
   Yes. See:

      * examples/outdoor_rest_kill_male_mosquitoes
      * examples/inputEIR
      * examples/ivermectin

Is there a drug campaign example? 
   Yes. See:

      * examples/drug_campaign
      * examples/diagnostic_survey

Is there a campaign sweep example? 
   Yes. See:

      * examples/campaign_sweep

Is there an example of creating a demographics file from scratch with the API?
    The best examples are currently in emodpy-measles and emodpy-hiv. We are working to add some to emod_api.demographics. The basic idea is you use one of 3 node creators, and then use the Setter API to set up the node defaults for fertility, mortality, age structure, initial immunity, individual 'risk', and initial prevalance. The first node creator, from_template_node, is very basic and usually for quickstarts or toy models. It lets you create a single node demographics file with a given population. The second creator, from_csv, lets you create a multinode demographics using a csv file with population data as an input. The third creator, from_params, lets you create a multinode demographics without specific node data but instead with a few parameters that represent the overall population and the population heterogeneity.

    This is what it could look like to use option 2::

        from emod_api.demographics import Demographics
        demog = Demographics.from_csv( input_csv_file )
        demog.SetConstantRisk()
        demog.SetInitialAgeLikeSubSaharanAfrica() 
        demog.generate_file(out_filename)
        return demog

Is there a demographics sweep example? 
   Yes. See:

      * examples/demographics_sweep

Is there a serialization/burn-in example? 
   Yes. See:

      * examples/burnin_create
      * examples/burnin_use

Is there a reporter configuration example? 
   Yes. See:

      * examples/add_reports
      * examples/filtered_report

What are some of the key differences for people used to using dtk-tools?
    1. Schema-Based. The creation of config and campaign files is entirely schema-based now. This means that you can only set parameters that the binary you are using recognizes. And parameter types and ranges are enforced at runtime.
    2. Inter-File Dependencies Now Automatic. Before there were lots of parameters in the config that you had to set to correspond to settings in campaign or demographics files. That is no longer the case. We call these 'implicits'. For example, if you add a BirthRate to the demographics, the corresponding parameters in the config.json (Enable_Births) will get set automatically for you. As another example, when you create a campaign and specify various 'events' to be broadcast/published and/or listened/subscribed to, you no longer have to figure out which ones are built-in and which are ad-hoc. It does that for you and populates the Custom_Events param on your behalf.
    3. Hierarchical Dependencies Now Automatic. If a parameter depends on another parameter, previously you had to set all the Enables in the dependency tree. Now they get set automatically for you. For example, if Enable_Birth is set (see above), Enable_Vital_Dynamics will be set for you.
    4. No JSON manipulation. dtk-tools worked primarily through manipulation of JSON that made up the configuration files. You no longer need to have any knowledge of the internal representation of data in the DTK input files. All configuration should be done via Python functions.
    5. Released and Installed Modules. We want users mostly using versioned released modules that have been pip installed, not git cloned, dev-installed code, except during development. The process of getting new code reviewed, tested, and getting the module versioned and released is intended to be smooth and efficient when everyone does their defined role. "Trust The Process and Do Your Job", as someone once said.
    6. Blessed Binaries. In dtk-tools you would often BYOB -- Bring Your Own Binary -- but in emodpy, the idea is that the system pulls down the latest CI (Continuous Integration) build for your disease that passed all the tests. We very much want to noramlize the idea of doing research with versioned software that has come through our professional BVT processes.

# emodpy-malaria
Python module for use as user-space front-end for doing research easily with EMOD (Malaria_SIM) via idmtools

## Documentation

Private documentation available at https://docs.idmod.org/projects/emodpy-malaria/en/latest/. Scroll to "Do you have a password? Access here" and use the password "IDM2020emodpy-malaria".

## FAQ

### Why does the system download a new Eradication binary (and supporting binaries/schema) each time I run?

The system is designed very much like you browse the web. When you go to a website/page, it downloads html, png and other files. If you go there again, it does it again. We don't even think about it (unless we have network issues). We want this to be the New Normal. You get the latest binary from Malaria-Ongoing branch that Passes All The Tests. That said, we know there are times when stasis and stability are paramount. To that end, you can pass a bamboo build number to 'get_model_files( plan, manifest )' and you'll always get that one.

### I want the super-secret way of just putting a binary (and corresponding schema) in the downloads directory and not doing any more downloads.

Just comment out the call to 'get_model_files'. 

### What is the purpose of the manifest.py file?

manifest.py is designed to house ALL your input and output paths in a single location. It also includes the path of your choice for where model binaries (and schema) are downloaded to and uploaded from. This is because even though you can happily ignore these files if you want, you'll have a better EMOD experience if you can easily reference the schema file and sometimes it's nice to be able to have access to the binary itself.

### How do I set config parameters?

Provide a param-setting function and pass that function to the emodpy task creator:
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L139

In that function, you can set parameters directly, e.g.
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L75

Or you can call a function in a standalone script that does the config params. E.g.,
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L65

### Are there defaults?

Great question. If you didn't set any config params at all, they will have defaults based on the schema.

But you can call emodpy_malaria.config.set_team_defaults. These defaults can be seen at:
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/ef806ca4cf27df5f42e99fc208b6ddd8ef745565/emodpy_malaria/config.py#L26

### How do I select/specify vector species for my scenario?

https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L66

### How do I set a vector species param value? Is there a helper function like set_species_param?

Here's an example:
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L72

But there is a request to add a helper function that makes this 'even easier'. Stay tuned.

### I see these calls to "finalize". What are those about and when do I need to do them?

They are going away very soon. Disregard.

### I pip installed emodpy-malaria, but I want to make changes. How should I do that?

python package_setup.py develop

There are some other options but that seems to be the most popular and proven. This means that the emodpy-malaria module in site-packages actually points to the same code as you have in your git checked-out repo. This link is useful for details: https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install#19048754.

But we want you to get the changes you like into the tested, versioned, released module before too long.

### I see lots of MALARIA_SIM examples. Are there any VECTOR_SIM examples?

Not at this time.

### I notice that I can import emod_api.campaign and use that as an object. I haven't seen that before.

Sure. Python modules are a lot like singletons. There's no need to add a static class inside that module in many cases. Think of the module (which can have variables and methods) as a static class.

### I want to just load a demographics.json, not create one programmatically.

OK, but be aware that one of the benefits of emodpy/emodapi is that you get guaranteed consistency between demographics settings and config params. But if you really want to use a raw demographics.json that you are very confident in, you can open that in your demog builder. An example of that is:

```
def build_demog():
    import emod_api.demographics.Demographics as Demographics
    demog = Demographics.from_file( "demographics.json" )
    return demog
```

### Why is it hanging on the Bamboo/downloading EXE step?
Make sure you are logged into the VPN.  If you aren't logged into the VPN, you can't access Bamboo and download the Eradication binaries (including pluglins and schema)

### How do I specify the number of cores? 

num_cores is an undocumented param to Platform(). It is not a DTK config param.

### How do I specify the log level for DTK? I get a schema error when I try to set it now.

TBD.

### the default_from_schema_no_validation.schema_to_config... is a little bit inscrutable. Can we hide this in a function?

TBD


# Known Issues.

The OS of the build plan and the OS of the target platform need to match. Right now it's possible to misconfigure and not be told until COMPS fails.

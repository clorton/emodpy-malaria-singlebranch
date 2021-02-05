# emodpy-malaria
Python module for use as user-space front-end for doing research easily with EMOD (Malaria_SIM) via idmtools

## Documentation

Private documentation available at https://docs.idmod.org/projects/emodpy-malaria/en/latest/. Scroll to "Do you have a password? Access here" and use the password "IDM2020emodpy-malaria".

## FAQ

# Why does the system download a new Eradication binary (and supporting binaries/schema) each time I run?

The system is designed very much like you browse the web. When you go to a website/page, it downloads html, png and other files. If you go there again, it does it again. We don't even think about it (unless we have network issues). We want this to be the New Normal. You get the latest binary from Malaria-Ongoing branch that Passes All The Tests. That said, we know there are times when stasis and stability are paramount. To that end, you can pass a bamboo build number to 'get_model_files( plan, manifest )' and you'll always get that one.

# I want the super-secret way of just putting a binary (and corresponding schema) in the downloads directory and not doing any more downloads.

Just comment out the call to 'get_model_files'. 

# What is the purpose of the manifest.py file?

manifest.py is designed to house ALL your input and output paths in a single location. It also includes the path of your choice for where model binaries (and schema) and downloaded to and uploaded from. This is because even though you can happily ignore these files if you want, you'll have a better EMOD experience if you can easily reference the schema file and sometimes it's nice to be able to have access to the binary itself.

# How do I set config parameters?

Provide a param-setting function and pass that function to the emodpy task creatorA
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L139

In that function, you can set parameters directly, e.g.
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L75.

Or you can call a function in a standalone script that does the config params. E.g.,
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L65

# Are there defaults?

Great question. If you didn't set any config params at all, they will have defaults based on the schema.

But you can call emodpy_malaria.config.set_team_defaults. These defaults can be seen at:
https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/ef806ca4cf27df5f42e99fc208b6ddd8ef745565/emodpy_malaria/config.py#L26

# How do I select/specify vector species for my scenario?

https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L66

# How do I set a vector species param value? Is there a helper function like set_species_param?

TBD





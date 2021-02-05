# emodpy-malaria
Python module for use as user-space front-end for doing research easily with EMOD (Malaria_SIM) via idmtools

## Documentation

Private documentation available at https://docs.idmod.org/projects/emodpy-malaria/en/latest/. Scroll to "Do you have a password? Access here" and use the password "IDM2020emodpy-malaria".

## FAQ

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

# How do I select/specifcy vector species for my scenario?

https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/examples/start_here/example.py#L66

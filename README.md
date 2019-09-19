This project aims to optimize dax build performance.
------------------

Build and setup a new virtual environment for dax. Implement cache mechanism during dax build (only on in dax build). Optimized code to remove unnecessary slow & duplicate url query. 

Summary:
------------
username: vuiisccidev

anaconda environment: /data/mcr/anaconda/dax/dax_new

activate virtual enviroment: source /data/mcr/dax_setup/dax_setup.sh

dax_new path: /data/mcr/dax_new

dax_new helper path: /data/mcr/dax_new_helper/. Place to store customized python packages. 

dax build new feature with cache on
------
dax build --project Project_ID --sessions Session_ID --cachedir /tmp/vuiisccidev/.webcache/ Project_settings.py

Step to create a new virtual environment for dax
--------

Migrate packages form old dax (/data/mcr/anaconda/dax/dax) to current environment: pip freeze > requirement.txt

Note: in old dax's, two global ".pth" are defined:

/data/mcr/anaconda/dax/dax/lib/python2.7/site-packages/masimatlab.pth

and

/data/mcr/anaconda/dax/dax/lib/python2.7/site-packages/dax.pth

Please make sure these files are edited correctly in new virtual environment. 

One more item: recon-stats has no available packages, need to manually re-install. 
  

For better maintenance: we place following packages on local with version control.

1. pyxnat: /data/mcr/dax_new_helper/pyxnat (https://github.com/MASILab/pyxnat, branch: vuiis_dax_build)

2. cachecontrol:/data/mcr/dax_new_helper/cachecontrol (https://github.com/MASILab/cachecontrol, branch: vuiis_dax_build)

3. recon-stats v1.0 source package for re-install


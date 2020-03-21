This project aims to optimize dax build performance.
------------------

Build and setup a new virtual environment for dax. Implement cache mechanism during dax build (only on in dax build). Optimized code to remove unnecessary slow & duplicate url query. 

Rename project dax_new to LDax for Legacy Distributed Automation for Xnat version - 03/03/2020

Megadocker update
------------
1. The vuiiscci_mega_docker_4.0.2-2020-03-19.img is not built from scratch. It is copied from vuiiscci_mega_docker_2.0.0-2018-11-28.img since old ldax uses mega_docker_2 to run all spiders.
2. We do not use vuiiscci_mega_docker_3.0.0-2018-11-28.img as a starting point is that, mega_docker_3 upgrade gclib. We can see the difference at /lib64. The upgrade will make FreeSurfer binary executable have segmentaion fault. The upgade in megadocker_3 was for obsolete surf_* spiders. Due to those surf_* have used Dax-1.0 yaml build, there is no way to keep maintaining megadocker_3.
3. There is no system library or new software installed in mega_docker_v4.0.2, update are all about python spider script and some text-base files. Here are a summary of update:

(1) /data/mcr/masimatlab/trunk/xnatspiders/spiders/Spider_fMRI_Preprocess.py
Just adding one line of code to make sure string array does not contain unicode. Shunxing modified on original spiders is due to such a minor change (it is probably not the best practice), and I don't want to generate a newer version of fMRI_Preprocess (i.e., Spider_fMRI_Preprocess_v1_0_0.py) to re-run whole the modified spiders on whole projects' sessions. 

(2) /data/mcr/masimatlab/trunk/xnatspiders/spiders/Spider_Cerebellum_Segmentation_v1_0_1.py
The updated cerebellum segmentation spiders. We find Spider_Cerebellum_Segmentation_v1_0_0.py original spider was modified in megadocker_v2 by Justin, which was inconsistent on SVN. For the reason of version control, Shunxing created a new Spider.

(3) /data/mcr/masimatlab/trunk/xnatspiders/spiders/Spider_Seeleyfmripreproc_v3_0_2.py
Fixed the Spider_Seeleyfmripreproc_v3_0_1.py issues on running sessions without T2 imaging.

(4) /data/mcr/masimatlab/trunk/xnatspiders/spiders/BLSA_hack/Spider_VBMQA.py
Maybe it is not the best practice again, but the Spider_VBMQA.py in spiders folder shares the same name in spiders/BLSA_hack folder. The reason for this is for version control, namely avoid running VBMQA higher verson on all sessions. The spiders/BLSA_hack/Spider_VBMQA.py was previously stored on masispider account's home directory. The content of that file is not the same with the one at SVN. So we made such a 'hacking' way.

(5) /data/mcr/ldax_setup/bashrc_ldax
A fresh bashrc which is supposed to be stored as /home/$USER/.bashrc

(6) /data/mcr/ldax_setup/matlab/start.m
A local backup for FreeSurfer set up.

job_template update
------------
(1) The ldax job template is stored at /home/vuiisccidev/.dax_template/job_template.txt
(2) Add session count to avoid too many Xnat download running at the same time. The current session max limit is 50.
(3) We stop using whole ACCRE's home, and just binding necessary setting files as follows. The bashrc has already stored in megadocekr (bashrc_ldax)
--bind /home/$USER/.dax_settings.ini:/home/$USER/.dax_settings.ini --bind /home/$USER/.daxnetrc:/home/$USER/.daxnetrc --bind /scratch/$USER:/scratch/$USER --bind /tmp:/tmp 
(4) The startup script of mega_docker_v4 is a bit change to setup bash and FreeSurfer environment
cp /data/mcr/ldax_setup/bashrc_ldax /home/vuiisccidev/.bashrc && \
source /home/vuiisccidev/.bashrc
cp -r /data/mcr/ldax_setup/matlab /home/vuiisccidev/ && \

ldax setup update (TODO)
------------

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

For vuiisccidev account -> use dax_manager, there is also an option '--cachedir' available.
If cachedir is not defined when call dax_manager, launcher would retrieve cachedir path at /home/vuiisccidev/.dax_cachedir, which is /tmp/vuiisccidev/.xnatcache/

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

3. recon-stats v1.0 source package for re-install  pip install git+https://github.com/MASILab/recon-stats.git@ldax


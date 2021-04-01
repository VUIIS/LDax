module load GCC/5.4.0-2.26
module load MATLAB/2017a
unset _JAVA_OPTIONS
FSLDIR=/data/mcr/fsl_510_eddy_511
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
. ${FSLDIR}/etc/fslconf/fsl.sh

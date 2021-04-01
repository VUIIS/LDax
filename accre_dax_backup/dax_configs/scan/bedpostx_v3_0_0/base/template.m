%% Runs the bedpostx pipeline
% Set environment
addpath(genpath('{justinlib_path}'));
addpath('{NIFTI_path}');
addpath('{bedpostx_path}');
addpath('{dwmri_visualizer_path}');
addpath('{distinguishable_colors_path}');

% Set job directory path
job_dir_path = '{job_dir_path}';

% Set up fsl
fsl_path = '{fsl_path}';

%% Run bedpostx pipeline

dwmri_path = '{dwmri_path}';
bvec_path = '{bvec_path}';
bval_path = '{bval_path}';
mask_path = '{mask_path}';

% bedpostx options
bedpostx_params = '{bedpostx_params}';

% Perform bedpostx pipeline
bedpostx_pipeline(job_dir_path, ...
                  dwmri_path, ...
                  bvec_path, ...
                  bval_path, ...
                  mask_path, ...
                  fsl_path, ...
                  bedpostx_params);

%% Remove PREPROCESSED and BEDPOSTX_DATA
preprocessed_dir = directory(job_dir_path,'PREPROCESSED');
preprocessed_dir.rm();

bedpostx_data_dir = directory(job_dir_path,'BEDPOSTX_DATA');
bedpostx_data_dir.rm();

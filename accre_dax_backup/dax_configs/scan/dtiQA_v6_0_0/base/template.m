%% Runs topup/eddy pipline, then runs the DTI stats pipeline
% Set environment
addpath(genpath('{justinlib_path}'));
addpath('{NIFTI_path}');
addpath('{topup_eddy_preprocess_path}');
addpath('{dti_stats_path}');
addpath('{dwmri_modelfit_path}');
addpath('{dwmri_visualizer_path}');
addpath('{distinguishable_colors_path}');

% Set job directory path
job_dir_path = '{job_dir_path}';

% Set FSL path
fsl_path = '{fsl_path}';

% Set camino path
camino_path = '{camino_path}';

% BET params
bet_params = '{bet_params}';

%% Run topup/eddy preprocessing pipeline

% Set dwmri_info - this will set base path to nifti/bvec/bval, phase encoding direction, and readout times
dwmri_info(n).base_path = '{dwmri_base_path;n}'; 
dwmri_info(n).pe_dir = '{dwmri_pe_dir;n}';
dwmri_info(n).readout_time = {dwmri_readout_time;n};
dwmri_info(n).scan_descrip = '{dwmri_scan_descrip;n}';

% ADC fix - apply it for Philips scanner
ADC_fix = {ADC_fix};

% zero_bval_thresh - will set small bvals to zero
zero_bval_thresh = {zero_bval_thresh};

% prenormalize - will prenormalize data prior to eddy
prenormalize = {prenormalize};

% use all b0s for topup
use_all_b0s_topup = {use_all_b0s_topup};

% topup params
topup_params = '{topup_params}';

% Sometimes name of eddy is 'eddy', 'eddy_openmp', or 'eddy_cuda'
eddy_name = '{eddy_name}';

% use b0s in eddy
use_b0s_eddy = {use_b0s_eddy};

% eddy params
eddy_params = '{eddy_params}';

% normalize - will normalize data and output a single B0
normalize = {normalize};

% Sort scans - will sort scans by b-value
sort_scans = {sort_scans};

% Set number of threads (only works if eddy is openmp version)
setenv('OMP_NUM_THREADS','{OMP_NUM_THREADS}');

% Make sure at least one "scan" exists
if ~any(strcmp('scan',{dwmri_info.scan_descrip}))
    error('At least one dwmri must be a "scan"');
end

% Test if first scan is a "b0"; if it is, set the first dwmri to be the 
% first "scan". This is because first diffusion image should correspond to 
% the first b0 for eddy.
if strcmp(dwmri_info(1).scan_descrip,'b0')
    first_scan_idx = find(strcmp({dwmri_info.scan_descrip},'scan'),1);
    disp(['Setting "scan": ' dwmri_info(first_scan_idx).base_path ' ' ...
          'in front because first dwmri is "b0": '  ...
          dwmri_info(1).base_path '. First dwmri should be a scan for eddy.']);
    % Rearrange
    dwmri_info = dwmri_info([first_scan_idx 1:first_scan_idx-1 first_scan_idx+1:length(dwmri_info)]);
end

% Go over and check each dwmri to see if the first scan is a b0; if not, 
% move the first b0 to the front.
for i = 1:length(dwmri_info)
    % Load bvals
    bvals = dlmread([dwmri_info(i).base_path '.bval']);
    b0_idx = find(bvals <= zero_bval_thresh);
    
    % Make sure first scan is a b0
    if isempty(b0_idx)
        error([dwmri_info(i).base_path ' does not have a b0!'])
    elseif b0_idx(1) ~= 1
        disp([dwmri_info(i).base_path '''s first scan isn''t a b0... ' ...
              'moving scan #' num2str(b0_idx(1)) ' to the front.'])
        idx_b0_front = [b0_idx(1) 1:b0_idx(1)-1 b0_idx(1)+1:length(bvals)];
        
        % Reorder bvals
        dlmwrite([dwmri_info(i).base_path '.bval'],bvals(idx_b0_front), ' ');        
        
        % Reorder bvecs
        bvecs = dlmread([dwmri_info(i).base_path '.bvec']);
        dlmwrite([dwmri_info(i).base_path '.bvec'],bvecs(:,idx_b0_front), ' ');     
                
        % Reorder nifti
        nifti_utils.idx_untouch_nii4D([dwmri_info(i).base_path '.nii.gz'], ...
                                      idx_b0_front, ...
                                      [dwmri_info(i).base_path '.nii.gz']);
    end
end

% Perform preprocessing
[dwmri_path,bvec_path,bval_path,mask_path,movement_params_path,topup_eddy_pdf_path] = topup_eddy_preprocess_pipeline(job_dir_path, ...
                                                                                                                     dwmri_info, ...
                                                                                                                     fsl_path, ...
                                                                                                                     ADC_fix, ...
                                                                                                                     zero_bval_thresh, ... 
                                                                                                                     prenormalize, ...
                                                                                                                     use_all_b0s_topup, ...
                                                                                                                     topup_params, ...
                                                                                                                     eddy_name, ...
                                                                                                                     use_b0s_eddy, ...
                                                                                                                     eddy_params, ...
                                                                                                                     normalize, ...
                                                                                                                     sort_scans, ...
                                                                                                                     bet_params);

%% Run dti stats pipeline

% CSF info
csf_info.label_path = '{csf_label_path}';
csf_info.template_path = '{csf_template_path}';
csf_info.template_masked_path = '{csf_template_masked_path}';

% Perform dti stats pipeline
dti_stats_pdf_path = dti_stats_pipeline(job_dir_path, ...
                                        dwmri_path, ...
                                        bvec_path, ...
                                        bval_path, ...
                                        mask_path, ...
                                        fsl_path, ...
                                        camino_path, ...
                                        csf_info, ... 
                                        bet_params, ...
                                        movement_params_path);

%% Merge PDFs
pdf_path = fullfile(job_dir_path,'PDF','dtiQA.pdf');
system_utils.system_with_errorcheck(['gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile=' pdf_path ' ' topup_eddy_pdf_path ' ' dti_stats_pdf_path ],'Failed to merge output PDFs');

% Remove single-paged pdfs
delete(topup_eddy_pdf_path);
delete(dti_stats_pdf_path);

%% Remove EDDY, DWMRI, and SCANS resource
eddy_dir = directory(job_dir_path,'EDDY');
eddy_dir.rm();

dwmri_dir = directory(job_dir_path,'DWMRI');
dwmri_dir.rm();

scans_dir = directory(job_dir_path,'SCANS');
scans_dir.rm();

%% Convert PREPROCESSED data to single precision
preprocessed_dir = directory(job_dir_path,'PREPROCESSED');
dwmri_file = file(preprocessed_dir,'dwmri.nii.gz');
dwmri_nii = load_untouch_nii(dwmri_file.get_path());

% Convert to single precision
dwmri_nii.hdr.dime.datatype = 16;
dwmri_nii.hdr.dime.bitpix = 32;
dwmri_nii.img = single(dwmri_nii.img);

% Save nifti
save_untouch_nii(dwmri_nii,dwmri_file.get_path());

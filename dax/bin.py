#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" File containing functions called by dax executables """

from __future__ import print_function

from builtins import str

from datetime import datetime
import imp
import os

from . import launcher
from . import log
from . import XnatUtils
from . import processors
from .dax_settings import DAX_Settings
from .errors import DaxError
DAX_SETTINGS = DAX_Settings()


def set_logger(logfile, debug):
    """
    Set the logging depth

    :param logfile: File to log output to
    :param debug: Should debug depth be used?
    :return: logger object

    """
    # Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax', logfile)
    else:
        logger = log.setup_info_logger('dax', logfile)
    return logger


def read_settings(settings_path, logger, exe):
    logger.info('Current Process ID: %s' % str(os.getpid()))
    msg = 'Current Process Name: dax.bin.{}({})'
    logger.info(msg.format(exe, settings_path))

    # Load the settings file
    logger.info('loading settings from: %s' % settings_path)
    if settings_path.endswith('.py'):
        settings = imp.load_source('settings', settings_path)
        dax_launcher = settings.myLauncher
    elif settings_path.endswith('.yaml'):
        dax_launcher = read_yaml_settings(settings_path, logger)
    else:
        raise DaxError('Wrong type of settings file given. Please use a \
python file describing the Launcher object or a YAML file.')

    # Run the updates
    logger.info('running launcher, Start Time: %s' % str(datetime.now()))
    return dax_launcher


def launch_jobs(settings_path, logfile, debug, projects=None, sessions=None,
                writeonly=False, pbsdir=None, force_no_qsub=False):
    """
    Method to launch jobs on the grid

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :param writeonly:  write the job files without submitting them
    :param pbsdir: folder to store the pbs file
    :param force_no_qsub: run the job locally on the computer (serial mode)
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    _launcher_obj = read_settings(settings_path, logger, exe='launch_jobs')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        _launcher_obj.launch_jobs(lockfile_prefix, projects, sessions,
                                  writeonly, pbsdir,
                                  force_no_qsub=force_no_qsub)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.LAUNCH_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception launching jobs in bin.launch_jobs')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.LAUNCH_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)

    logger.info('finished launcher, End Time: %s' % str(datetime.now()))


def build(settings_path, logfile, debug, cachedir,projects=None, sessions=None,
          mod_delta=None, proj_lastrun=None):
    """
    Method that is responsible for running all modules and putting assessors
     into the database

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be built
    :param sessions: Session(s) that need to be built
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)
    _launcher_obj = read_settings(settings_path, logger, exe='build')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        # SHUNXING add cachedir option to build function argument
        _launcher_obj.build(lockfile_prefix, cachedir, projects, sessions,
                            mod_delta=mod_delta, proj_lastrun=proj_lastrun)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.BUILD_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception building Project in bin.build')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.BUILD_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)

    logger.info('finished build, End Time: %s' % str(datetime.now()))


def update_tasks(settings_path, logfile, debug, projects=None, sessions=None):
    """
    Method that is responsible for updating a Task.

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    _launcher_obj = read_settings(settings_path, logger, exe='update_tasks')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        _launcher_obj.update_tasks(lockfile_prefix, projects, sessions)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.UPDATE_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception updating tasks in bin.update_tasks')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))
        flagfile = os.path.join(os.path.join(
            DAX_SETTINGS.get_results_dir(), 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.UPDATE_SUFFIX))
        _launcher_obj.unlock_flagfile(flagfile)

    logger.info('finished updating tasks, End Time: %s' % str(datetime.now()))


def pi_from_project(project):
    """
    Get the last name of PI who owns the project on XNAT

    :param project: String of the ID of project on XNAT.
    :return: String of the PIs last name

    """
    pi_name = ''
    with XnatUtils.get_interface() as xnat:
        proj = xnat.select.project(project)
        pi_name = proj.attrs.get('xnat:projectdata/pi/lastname')

    return pi_name


def read_yaml_settings(yaml_file, logger):
    """
    Method to read the settings yaml file and generate the launcher object.

    :param yaml_file: path to yaml file defining the settings
    :return: launcher object
    """
    if not os.path.isfile(yaml_file):
        err = 'Path not found for {}'
        raise DaxError(err.format(yaml_file))

    doc = XnatUtils.read_yaml(yaml_file)

    # Set Inputs from Yaml
    check_default_keys(yaml_file, doc)

    # Set attributs for settings:
    attrs = doc.get('attrs')

    # Read modules and processors:
    mods = dict()
    modules = doc.get('modules', list())
    for mod_dict in modules:
        if mod_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(mod_dict.get('name'))
            raise DaxError(err)
        mods[mod_dict.get('name')] = load_from_file(
            mod_dict.get('filepath'), mod_dict.get('arguments'), logger)
    procs = dict()
    processors = doc.get('processors', list())
    for proc_dict in processors:
        if proc_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(proc_dict.get('name'))
            raise DaxError(err)
        procs[proc_dict.get('name')] = load_from_file(
            proc_dict.get('filepath'), proc_dict.get('arguments'), logger)
    yamlprocs = dict()
    yamls = doc.get('yamlprocessors', list())
    for yaml_dict in yamls:
        if yaml_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(yaml_dict.get('name'))
            raise DaxError(err)
        yamlprocs[yaml_dict.get('name')] = load_from_file(
            yaml_dict.get('filepath'), yaml_dict.get('arguments'), logger)

    # project:
    proj_mod = dict()
    proj_proc = dict()
    yaml_proc = dict()
    projects = doc.get('projects')
    for proj_dict in projects:
        project = proj_dict.get('project')
        if project:
            # modules:
            if proj_dict.get('modules'):
                for mod_n in proj_dict.get('modules').split(','):
                    if project not in list(proj_mod.keys()):
                        proj_mod[project] = [mods[mod_n]]
                    else:
                        proj_mod[project].append(mods[mod_n])

            # processors:
            if proj_dict.get('processors'):
                for proc_n in proj_dict.get('processors').split(','):
                    if project not in list(proj_proc.keys()):
                        proj_proc[project] = [procs[proc_n]]
                    else:
                        proj_proc[project].append(procs[proc_n])

            # yaml_proc:
            if proj_dict.get('yamlprocessors'):
                for yaml_n in proj_dict.get('yamlprocessors').split(','):
                    if project not in list(yaml_proc.keys()):
                        yaml_proc[project] = [yamlprocs[yaml_n]]
                    else:
                        yaml_proc[project].append(yamlprocs[yaml_n])

    # set in attrs:
    attrs['project_process_dict'] = proj_proc
    attrs['project_modules_dict'] = proj_mod
    attrs['yaml_dict'] = yaml_proc

    return launcher.Launcher(**attrs)


def check_default_keys(yaml_file, doc):
    """ Static method to raise error if key not found in dictionary from
    yaml file.
    :param yaml_file: path to yaml file defining the processor
    :param doc: doc dictionary extracted from the yaml file
    """
    # processors / modules / yamlprocessors are not required
    for key in ['projects', 'attrs']:
        raise_yaml_error_if_no_key(doc, yaml_file, key)


def raise_yaml_error_if_no_key(doc, yaml_file, key):
    """Method to raise an execption if the key is not in the dict
    :param doc: dict to check
    :param yaml_file: YAMLfile path
    :param key: key to search
    """
    if key not in list(doc.keys()):
        err = 'YAML File {} does not have {} defined. See example.'
        raise DaxError(err.format(yaml_file, key))


def load_from_file(filepath, args, logger):
    """
    Check if a file exists and if it's a python file
    :param filepath: path to the file to test
    :return: True the file pass the test, False otherwise
    """
    if args is not None:
        _tmp = 'test.{}(**args)'
    else:
        _tmp = 'test.{}()'

    if not os.path.isfile(filepath):
        raise DaxError('File %s does not exists.' % filepath)

    if filepath.endswith('.py'):
        test = imp.load_source('test', filepath)
        try:
            return eval(_tmp.format(test.__processor_name__))
        except AttributeError:
            pass

        try:
            return eval(_tmp.format(os.path.basename(filepath)[:-3]))
        except AttributeError:
            pass

        err = '[ERROR] Module or processor NOT FOUND in the python file {}.'
        logger.error(err.format(filepath))

    elif filepath.endswith('.yaml'):
        return processors.AutoProcessor(filepath, args)

    return None

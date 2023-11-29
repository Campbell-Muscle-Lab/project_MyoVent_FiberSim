# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import shutil
import json
import os

from pathlib import Path

import numpy as np

import multiprocessing
import threading
import subprocess


def generate_protocols():
    """ Generates protocols of different lengths """
    
    top_dir = 'd:/ken/github/campbellmusclelab/projects/project_myovent_fibersim'
    
    model_file = 'base/model_fs_smooth.json'
    options_file = 'base/options.json'
    protocol_file = 'base/protocol.json'
    results_dir = 'sim_data'
    output_handler_file = 'base/output_handler.json'
    generated_dir = 'generated'
    exe_file = 'd:/ken/github/campbellmusclelab/models/myovent/code/myoventcpp/bin/myoventcpp.exe'
    
    MyoVentPy_code_dir = 'd:/ken/github/campbellmusclelab/models/myovent/code/myoventpy/myoventpy'
    
    figures_only = ''
    
    prot_points = np.int32(1000 * (np.linspace(10, 800, num=20)))
    # prot_points = [12000]
    
    
    # Make and clean the generated folder
    generated_dir = os.path.join(top_dir, generated_dir)
    try:
        print('Trying to remove %s' % generated_dir)
        shutil.rmtree(generated_dir, ignore_errors = True)
    except OSError as e:
        print('Error: %s : %s' % (generated_dir, e.strerror))
        
    if not os.path.isdir(generated_dir):
        os.makedirs(generated_dir)
        
    # Clean and make the sim_data folder
    results_dir = os.path.join(top_dir, results_dir)
    
    try:
        print('Trying to remove %s' % results_dir)
        shutil.rmtree(results_dir, ignore_errors = True)
    except OSError as e:
        print('Error: %s : %s' % (results_dir, e.strerror))
        
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    
    # Get the original protocol and output handler files
    orig_protocol_file = os.path.join(top_dir, protocol_file)
    orig_output_handler_file = os.path.join(top_dir, output_handler_file)
    
    # Create the batch            
    batch = dict()
    batch['MyoVent_batch'] = dict()
    batch['MyoVent_batch']['MyoVentCpp_exe'] = dict()
    batch['MyoVent_batch']['MyoVentCpp_exe']['exe_file'] = exe_file
    
    command_strings = []
    
    for (i,pp) in enumerate(prot_points):
        
        job = []
        
        with open(orig_protocol_file, 'r') as f:
            new_prot = json.load(f)
            
        new_prot['protocol']['no_of_time_steps'] = int(pp)
        
        new_protocol_file = os.path.join(
            top_dir,
            generated_dir,
            ('protocol_%i.json' % (i+1)))
        
        with open(new_protocol_file, 'w') as f:
            json.dump(new_prot, f, indent=4)
            
        with open(orig_output_handler_file, 'r') as f:
            oh = json.load(f)
            
        oh['templated_images'][0]['output_file_string'] = \
            os.path.join(results_dir,
                         ('sim_output_%i.png' % (i+1)))
            
        new_output_handler_file = os.path.join(
            top_dir,
            generated_dir,
            ('output_handler_%i.json' % (i+1)))
        
        with open(new_output_handler_file, 'w') as f:
            json.dump(oh, f, indent=4)
        
        j = dict()
        j['model_file'] = os.path.join(top_dir, model_file)
        j['options_file'] = os.path.join(top_dir, options_file)
        j['protocol_file'] = new_protocol_file
        j['results_file'] = os.path.join(results_dir,
                                         ('sim_output_%i.txt' % (i+1)))
        j['output_handler_file'] = new_output_handler_file
        
        job.append(j)
        
               
        batch['MyoVent_batch']['job'] = job
    
        new_batch_file_string = os.path.join(generated_dir,
                                         ('batch_%i.json' % (i+1)))
    
        with open(new_batch_file_string, 'w') as f:
            json.dump(batch, f, indent=4)
            
        cs = "pushd \"%s\" & python MyoVentPy.py run_batch %s %s & popd" % \
            (MyoVentPy_code_dir, new_batch_file_string, figures_only)
        
           
        command_strings.append(cs)
        
    print(command_strings)
            
    
    # Get max threads available
    available_threads = multiprocessing.cpu_count()-1

    # Set processes to mininmum of requested and available
    num_processes = available_threads
    print('Running batch using %i threads' % num_processes)

    if (not figures_only):
        # Now run the batch
        my_list = command_strings
    
        threads = []
        while threads or my_list:
            if (len(threads) < num_processes) and my_list:
                t = threading.Thread(target=worker, args=[my_list.pop()])
                t.daemon = True
                t.start()
                threads.append(t)
            else:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)  
        
def worker(cmd):
    print('\n')
    print(cmd)
    os.system(cmd)

        
if __name__ == "__main__":
    generate_protocols()   
            
        
        
        
        
        
    
    


    
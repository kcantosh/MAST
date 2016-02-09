##############################################################
# This code is part of the MAterials Simulation Toolkit (MAST)
# 
# Maintainer: Tam Mayeshiba
# Last updated: 2016-02-08
##############################################################
##############################################################
# Requirements:
# 1. Home directory access from where the test will be run
# 2. MAST installation
##############################################################
import os
import time
import shutil
import numpy as np
from MAST.utility import MASTError
from MAST.utility import dirutil
from MAST.utility import MASTFile
import MAST
import subprocess
testname ="workflow_test"
testdir = dirutil.get_test_dir(testname)
checkname = os.path.join(testdir, "WORKFLOW_CONFIG")

def verify_checks():
    checkfile=MASTFile(checkname)
    for myline in checkfile.data:
        if "Check" in myline:
            checkresult = myline.split(":")[1].strip()[0].lower()
            if checkresult == 'y':
                print "Checks okay"
            else:
                raise MASTError("verify checks","Checks for workflow setup not verified. Check %s" % checkname)
    return

def get_variables():
    verify_checks()
    myvars=dict()
    checkfile=MASTFile(checkname)
    for myline in checkfile.data:
        if myline[0:9] == "workflow_":
            mykey = myline.split("=")[0].strip()
            myval = myline.split("=")[1].strip()
            myvars[mykey] = myval
    return myvars

def create_workflow_test_script(inputfile):
    myvars = get_variables()
    # set up testing directory tree
    timestamp=time.strftime("%Y%m%dT%H%M%S")
    wtdir=myvars['workflow_test_directory']
    mast_test_dir = os.path.join(wtdir,"workflow_test_%s" % timestamp)
    shutil.copytree("%s/mini_mast_tree" % wtdir, mast_test_dir)
    # set up output file and submission script
    shortname = inputfile.split(".")[0]
    output="%s/output_%s" % (wtdir, shortname)
    submitscript="%s/submit_%s.sh" % (wtdir, shortname)
    generic_script="%s/generic_mast_workflow.sh" % wtdir
    bashcommand="bash %s %s %s %s %s %s >> %s" % (generic_script,
            mast_test_dir,
            myvars["workflow_examples_located"],
            inputfile,
            myvars["workflow_activate_command"],
            myvars["workflow_testing_environment"],
            output)
    scriptfile = MASTFile(os.path.join(wtdir, "submit_stub.sh"))
    scriptfile.data.append("\n")
    scriptfile.data.append(bashcommand + "\n")
    scriptfile.to_file(submitscript)
    
    return [mast_test_dir, submitscript, output]

def generic_submit(inputfile):
    [mast_test_dir, submitscript, outputname] = create_workflow_test_script(inputfile)
    
    myqsub = MAST.submit.queue_commands.queue_submission_command(submitscript)
    qproc = subprocess.Popen(myqsub, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    qproc.wait()
    
    if not (os.path.isfile(outputname)):
        raise OSError("Test did not create output %s" % outputname)
    waitct=0
    tailcmd = "tail -n 3 %s" % outputname
    maxwait=502
    while waitct < maxwait:
        tail3proc=subprocess.Popen(tailcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tail3=tail3proc.communicate()[0]
        tail3proc.wait()
        for tailline in tail3.split("\n"):
            if "Workflow completed" in tailline:
                return ["Completed", mast_test_dir]
        time.sleep(30)
        waitct = waitct + 1
        print "Output not complete. Attempt %i/%i" % (waitct, maxwait)
    return ["Unfinished", mast_test_dir]

def get_finished_recipe_dir(mast_test_dir):
    trydirs=os.listdir(os.path.join(mast_test_dir,"ARCHIVE"))
    for trydir in trydirs:
        trypath=os.path.join(mast_test_dir,"ARCHIVE",trydir)
        if (os.path.isdir(trypath)):
            return trypath
    return ""

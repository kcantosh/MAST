from MAST.utility.picklemanager import PickleManager
from MAST.parsers.recipeparsers import RecipeParser
from MAST.recipe.recipesetup import RecipeSetup
from MAST.recipe.recipe_plan import RecipePlan
import sys
import subprocess
import os
# this script location /home/hwkim/MAST4pymatgen/test/dagtest
print "=============================================================="
print "Let me assume that this script is run in that script location"
print "Right now I do not know how to set the directory for output"
print "=============================================================="

# The
argv=[]
mastrootdir = os.environ['SCRIPTPATH']
print 'mast root directory : '+mastrootdir
binpath = os.path.join(mastrootdir,'bin/mast')
bindir= os.path.join(mastrootdir,'bin')
print 'bindir : '+bindir
print 'binpath : '+binpath
inputfile = os.path.join(mastrootdir,'test/full_workflow_test/test.inp')

print 'input directory : ' + inputfile
argv.append('-i')
argv.append(inputfile)
#sys.path.append(bindir)
#import mast_test
#mast_test.main(argv[0],argv[1])
subprocess.call([sys.executable, binpath, argv[0],argv[1]])

pm = PickleManager()
mastobj = pm.load_variable('mast.pickle')
mastobj.ingreidient
depdict = mastobj.dependency_dict
ingredients = mastobj.ingredients
njobs = len(ingredients)

from MAST.DAG.dagscheduler import DAGScheduler
from MAST.DAG.dagscheduler import JobEntry
from MAST.DAG.dagscheduler import DAGParser
from MAST.DAG.dagscheduler import SessionEntry
from MAST.DAG.dagscheduler import JobEntry
from MAST.DAG.dagscheduler import JobTable
from MAST.DAG.dagscheduler import SessionTable
from MAST.DAG.dagscheduler import set2str
# seession id
jt = JobTable()
st = SessionTable()

sid = 1
s1 = SessionEntry(sid=sid,totaljobs=njobs)
st.addsession(s1)
jobnames = ingredients.keys()
jobname_id = {}
resultrootdir = '/home/hwkim/MAST4pymatgen/test/dagtest/'
sessiondir = os.path.join(resultrootdir,str(sid))
for jid in range(njobs):
    jobdir=os.path.join(sessiondir,jobnames[jid])
    jtype = type(ingredients[jobnames[jid]])
    ajob = JobEntry(sid=sid, jid=jid+1, jobname=jobnames[jid],indir=jobdir,outdir=jobdir,type=jtype)
    jt.addjob(ajob)
    jobname_id[jobnames[jid]]=jid+1

for child, parent in depdict.iteritems():
    for aparent in parent:
        print child +"<="+ aparent
        print str(jobname_id[child])+"<="+ str(jobname_id[aparent])
        jt.jobs[jobname_id[child]].addparent(jobname_id[aparent])
    

                  
#pm = Picklemanager()
#rp = pm.load_variable('mast.pickle')

#setup_obj = RecipeSetup(recipeFile='test-recipe.txt')
#recipe_plan_obj = setup_obj.star()
 

#!/bin/sh
#
# Force Bourne Shell if not Sun Grid Engine default shell (you never know!)
#
#$ -S /bin/sh
#
# I know I have a directory here so I'll use it as my initial working directory
#
#$ -wd /vol/grid-solar/sgeusers/currieferg 
#
# End of the setup directives
#
# Now let's do something useful, but first change into the job-specific
# directory that should have been created for us
#
# Check we have somewhere to work now and if we don't, exit nicely.
#

echo $1

if [ -d /local/tmp/currieferg/$JOB_ID.$SGE_TASK_ID ]; then
        cd /local/tmp/currieferg/$JOB_ID.$SGE_TASK_ID
else
        echo "Uh oh ! There's no job directory to change into "
        echo "Something is broken. I should inform the programmers"
        echo "Save some information that may be of use to them"
        echo "There's no job directory to change into "
        echo "Here's LOCAL TMP "
        ls -la /local/tmp
        echo "AND LOCAL TMP currieferg "
        ls -la /local/tmp/currieferg
        echo "Exiting"
        exit 1
fi
#
# Now we are in the job-specific directory so now can do something useful
#
# Stdout from programs and shell echos will go into the file
#    scriptname.o$JOB_ID.$SGE_TASK_ID
#  so we'll put a few things in there to help us see what went on
#
echo ==UNAME==
uname -n
echo ==WHO AM I and GROUPS==
id
groups
echo ==SGE_O_WORKDIR==
echo $SGE_O_WORKDIR
echo ==/LOCAL/TMP==
ls -ltr /local/tmp/
echo ==/VOL/GRID-SOLAR==
ls -l /vol/grid-solar/sgeusers/
#
# OK, where are we starting from and what's the environment we're in§   
#
echo ==RUN HOME==
pwd
ls
echo ==ENV==
env
echo ==SET==
set
#
echo == WHATS IN LOCAL/TMP ON THE MACHINE WE ARE RUNNING ON ==
ls -ltra /local/tmp | tail
#
echo == WHATS IN LOCAL TMP currieferg JOB_ID AT THE START==
ls -la 
#
# Copy the input file to the local directory
#
cp -r /vol/grid-solar/sgeusers/currieferg/* . # copy everything? 
echo ==WHATS THERE HAVING COPIED STUFF OVER AS INPUT==
ls -la 
#
# Move into implementations
#
if [ -d /local/tmp/currieferg/$JOB_ID.$SGE_TASK_ID/Implementations ]; then
        cd /local/tmp/currieferg/$JOB_ID.$SGE_TASK_ID/Implementations 
fi
# 
# Note that we need the full path to this utility, as it is not on the PATH
#
python grid_run_a_task_wrapper.py $JOB_ID $SGE_TASK_ID $1
#
echo ==AND NOW, HAVING DONE SOMTHING USEFUL AND CREATED SOME OUTPUT==
ls -la
#
# Now we move the output to a place to pick it up from later
#  noting that we need to distinguish between the TASKS
#  (really should check that directory exists too, but this is just a test)
#
cp -a results_file/* /vol/grid-solar/sgeusers/currieferg/Implementations/results_file/
#
echo "Ran through OK"

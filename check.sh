# first argument passed should be the genome used
genome="$1"
# load our shared variables
source vars.sh
# our expected to exist features file
bbed="$PIXI_PROJECT_ROOT/hub/${genome}/features.bb"
# the bed file to be created
cbed="$cache/check.bed"

# create the bed file to check
bigBedToBed $bbed $cbed
# cat out the bed file
cat $cbed

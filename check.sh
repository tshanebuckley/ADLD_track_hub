# first argument passed should be the genome used
genome="$1"
# cache directory
cache="$PIXI_PROJECT_ROOT/.cache"
# our expected to exist features file
bbed="$PIXI_PROJECT_ROOT/hub/${genome}/features.bb"
# the bed file to be created
bed="$cache/check.bed"

# create the bed file to check
bigBedToBed $bbed $bed
# cat out the bed file
cat $bed

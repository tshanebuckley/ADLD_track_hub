# set the genome to the first argument passed
genome="$1"
# load our shared variables
source vars.sh
# chrom sizes file
chrom="$cache/${genome}.chrom.sizes"
# reference genome dir in the hub
ref="$hub/$genome"
# big bed file
bbed="$ref/features.bb"
# trackDb file base
bdb="$data/$genome/trackDb.txt"
# trackDb file in the hub itself
db="$ref/trackDb.txt"

# create the cache dir if it doesn't exist
mkdir -p $cache

# fetch the chrom sizes
fetchChromSizes $genome > $chrom
# strip the headers from the bed file
grep -v "^browser\|^track\|^#" $bed | sed '/^[[:space:]]*$/d; s/\r//' | awk -v OFS='\t' '{$1=$1; print}' > $xbed
# run the python cli tool to:
# 1. append the trackDb line for our data table extension columns
# 2. generate out the AutoSQL file with our extension columns
# 3. append the formatted data columns to our bed file
adld $genome $data $hub $xbed
# create the big bed file
bedToBigBed -sort -type=bed9+ $xbed $chrom $bbed

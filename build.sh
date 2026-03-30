# set the genome to the first argument passed
genome="$1" 
# track hub root
hub="$PIXI_PROJECT_ROOT/hub"
# data directory
data="$PIXI_PROJECT_ROOT/data"
# cache for each build
cache="$PIXI_PROJECT_ROOT/.cache"
# chrom sizes file
chrom="$cache/${genome}.chrom.sizes"
# bed file
bed="$data/data.bed"
# headerless bed file
xbed="$cache/features.bed"
# big bed file
bbed="$hub/${genome}/features.bb"

# create the cache dir if it doesn't exist
mkdir -p $cache

# fetch the chrom sizes
fetchChromSizes $genome > $chrom
# strip the headers from the bed file
grep -v "^browser\|^track\|^#" $bed | sed '/^[[:space:]]*$/d; s/\r//' > $xbed
# create the big bed file
bedToBigBed -sort -type=bed9+ $xbed $chrom $bbed

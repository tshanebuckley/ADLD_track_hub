
table features
"ADLD extended features"
(
    string  chrom;  "Chromosome"
    uint    chromStart; "Start position"
    uint    chromEnd;   "End position"
    string  name;   "Feature name"
    uint    score;  "Score 0-1000"
    char[1] strand; "Strand"
    uint    thickStart; "Thick start"
    uint    thickEnd;   "Thick end"
    uint    reserved;   "ItemRgb"
    lstring    jsonmolecular;    "Key-value pairs displayed as detail table"
)
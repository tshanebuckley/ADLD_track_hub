from pydantic import BaseModel, TypeAdapter
from abc import ABC
from typing import List
import csv
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Type
import importlib
import importlib.util
from importlib.abc import Loader
import sys
import json
import yaml
from pathlib import Path
import shutil
import polars as pl
from jinja2 import Template

auto_sql_template: str = """
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
    {{extensions}}
)
"""

bed_columns: List[str] = [
    "chrom",
    "chromStart",
    "chromEnd",
    "name",
    "score",
    "strand",
    "thickStart",
    "thickEnd",
    "reserved"
]

# Data contained by the rows of a table. Loaded through a Pydantic
# object to validate data at runtime of track hub building. Ultimitely,
# we are looking to load a list of these to be converted to the track hub
# text format for tablar data.
class RowData(ABC, BaseModel):
    # all of these should at least contain "name" to merge on
    name: str

# The meta data loaded from the yaml sibling file of the csv file.
class TableMetaData(BaseModel):
    table_name: str
    column_name: str
    description: str | None

# Small class containing the results needed to extend the trackDb.txt
# and AutoSQL files.
class RowBuildReturn:
    track_db: str
    auto_sql: str
    data: pl.DataFrame

    def __init__(self, track_db: str, auto_sql: str, data: pl.DataFrame):
        self.track_db = track_db
        self.auto_sql = auto_sql
        self.data = data

# The data structure to load that will contain both the meta data
# and the data rows for the bed data extension.
class BedTableExtension:
    meta: TableMetaData
    extensions: List[RowData]

    def __init__(self, table: Path):
        self.meta = load_meta(table)
        self.extensions = load_extension(table)

    # Converts the RowData list into a polars DataFrame.
    def as_dataframe(self) -> pl.DataFrame:
        rows = []
        for model in self.extensions:
            data = model.model_dump()
            name = data.pop("name")
            rows.append({"name": name, self.meta.column_name: str(data)})
        return pl.DataFrame(rows)

    # Gets the string to append to the trackDb.txt file.
    def get_track_db_append(self) -> str:
        return f"json{self.meta.column_name}|{self.meta.table_name}"

    # Gets the string to append to the features.as file.
    def get_auto_sql_append(self) -> str:
        description = self.meta.description
        if description == None or description == "":
            description = "Key-value pairs displayed as detail table"
        return f"lstring    json{self.meta.column_name};    \"{description}\""

    def build(self) -> RowBuildReturn:
        return RowBuildReturn(
            track_db = self.get_track_db_append(),
            auto_sql = self.get_auto_sql_append(),
            data = self.as_dataframe()
        )

# Contains the original bed file data and the bed file extensions.
class BedTable:
    data: pl.DataFrame
    extensions: List[BedTableExtension]
    template: Path
    hub: Path
    bed: Path

    def __init__(self, path: Path, hub: Path, reference: str, bed: Path):
        self.template = path / reference
        self.hub = hub / reference
        self.bed = bed
        tables: Path = path / "tables"
        # load the actual bed file
        self.data = load_bed(bed)
        # load the extensions
        self.extensions = []
        extensions: List[Path] = [f for f in tables.iterdir() if f.is_dir()]
        for extension in extensions:
            self.extensions.append(
                BedTableExtension(
                    extension
                )
            )

    def build(self):
        trackDb: List[str] = []
        autoSQL: List[str] = []
        bed: pl.DataFrame = self.data
        for extension in self.extensions:
            extension_results = extension.build()
            # join the bed extensions to the main bed file
            bed = bed.join(
                extension_results.data,
                on="name",
                how="left"
            )
            bed.write_csv(
                self.bed,
                separator = "\t",
                include_header = False
            )
            # collect the trackDb append line for the tables
            trackDb.append(extension_results.track_db)
            # collect the variables to insert into the AutoSQL schema
            autoSQL.append(extension_results.auto_sql)

        db: Path = self.hub / "trackDb.txt"
        # copy over the template trackDb.txt file
        shutil.copy(
            self.template / "trackDb.txt",
            db
        )
        # append the trackDb.txt file
        with open(db, "a") as file:
            file.write(f"detailsDynamicTable {','.join(trackDb)}\n")
        # generate the AutoSQL file
        template = Template(auto_sql_template)
        with open(self.hub / "features.as", "w") as file:
            file.write(
                template.render(
                    extensions = "\n".join(autoSQL)
                )
            )

# The path to the folder containing the meta.yaml file.
def load_meta(table: Path) -> TableMetaData:
    with open(table / 'meta.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return TableMetaData.model_validate(data)

# The path to the folder containing the schema.py and data.csv sibling files.
def load_extension(table: Path) -> List[RowData]:
    try:
        # use the name of the folder as the module name
        module_name = table.name
        schema: Path = table / "schema.py"
        data: Path = table / "data.csv"
        # 1. Create a module specification (spec) from the file path
        spec: ModuleSpec|None = importlib.util.spec_from_file_location(module_name, schema)
        # 2. Create a new module object based on that spec
        module: ModuleType
        if isinstance(spec, ModuleSpec):
            module = importlib.util.module_from_spec(spec)
            # 3. (Optional but Recommended) Add module to sys.modules
            # This allows the module to handle its own internal imports correctly
            sys.modules[module_name] = module
            # 4. Execute the module in its own namespace to populate it
            loader: Loader|None = spec.loader
            if isinstance(loader, Loader):
                loader.exec_module(module)
                # 5. Retrieve and return the class
                cls: Type[RowData] = getattr(module, "Schema")
                # 6. Load the list of RowData objects, validating them
                with open(table / "data.csv", "r") as f:
                    reader = csv.DictReader(f)
                    rows = [cls.model_validate(row) for row in reader]
                return rows
            else:
                raise Exception("Module loader not found.")
        else:
            raise Exception("Module object failed to load.")
    except ModuleNotFoundError as e:
        print(f"Module '{table}' doesn't exist.")
        raise e
    except TypeError as e:
        print(f"Error: {e}")
        raise e

# Helper method to load the bed data from the root data directory.
def load_bed(path: Path) -> pl.DataFrame:
    return pl.read_csv(
        path,
        has_header = False,
        new_columns = bed_columns,
        separator = "\t"
    )

# Iterates over a directory of the following format:
# data
# |- data.bed
# |- extension1
# |   |- data.csv => contains the actual data for this data table extension
# |   |- meta.yaml => contains some meta data for implementing the extension
# |   |- schema.py => contains a class named "Schema" implementing RowData
# |- extension2
# |   |- data.csv
# |   |- meta.yaml
# |   |- schema.py
# ...
# |- extensionN
#     |- data.csv
#     |- meta.yaml
#     |- schema.py
# building an initial bed file with the extensions provided
# into a track hub with an appropriately formated features.as
# and trackDb.txt files along with a bed file. After this step,
# all that remains is building the bigBed file and pushing to
# GitHub to host.
def build_hub(path: Path, hub: Path, reference: str, bed: Path):
    # create a BedTable object
    b = BedTable(path, hub, reference, bed)
    # commit the actual changes out to files
    b.build()

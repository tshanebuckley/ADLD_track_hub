import typer
from pathlib import Path
from typing import Annotated
import polars as pl

from adld_track_hub.utils.models import build_hub

app = typer.Typer()

@app.command()
def main(
    reference: str,
    data: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            help="Input file to process"
        )
    ],
    hub: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            help="Input file to process"
        )
    ],
    bed: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="Input file to process"
        )
    ]
):
    build_hub(data, hub, reference, bed)
    print(f"Hello")

if __name__ == "__main__":
    app()

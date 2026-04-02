from adld_track_hub.utils.models import RowData

class Schema(RowData):
    variant_type: str
    disease_association: str | None
    size: str
    orientation: str | None
    junction_start: str | None
    junction_end: str | None
    repeats: str | None # Yes or No
    microhomology: str| None
    detection_method: str | None
    three_prime_primer: str | None
    five_prime_primer: str | None

from typing import NamedTuple, Optional, Tuple


class FilterSettings(NamedTuple):
    title: str
    label_fields: Tuple[str]
    api_endpoint: Optional[str] = None
    depends_on: Optional[str] = None
    query_name: Optional[str] = None

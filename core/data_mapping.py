from typing import Dict, List, Any
import json

class DataPoint:
    def __init__(self, protocol: str, tag: Dict[str, Any], name: str = ""):
        self.protocol = protocol
        self.tag = tag
        self.name = name or f"{protocol}_{tag.get('address', '')}"

class DataMapping:
    def __init__(self):
        self.mappings: List[Dict[str, DataPoint]] = []

    def add_mapping(self, source: DataPoint, destination: DataPoint):
        self.mappings.append({
            "source": source,
            "destination": destination,
            "enabled": True,
            "transformation": None
        })

    def remove_mapping(self, index: int):
        if 0 <= index < len(self.mappings):
            self.mappings.pop(index)

    def set_transformation(self, index: int, transform_function: str):
        if 0 <= index < len(self.mappings):
            self.mappings[index]["transformation"] = transform_function

    def save_to_file(self, filename: str):
        data = []
        for mapping in self.mappings:
            data.append({
                "source": {
                    "protocol": mapping["source"].protocol,
                    "tag": mapping["source"].tag,
                    "name": mapping["source"].name
                },
                "destination": {
                    "protocol": mapping["destination"].protocol,
                    "tag": mapping["destination"].tag,
                    "name": mapping["destination"].name
                },
                "enabled": mapping["enabled"],
                "transformation": mapping["transformation"]
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.mappings = []
        for item in data:
            source = DataPoint(
                item["source"]["protocol"],
                item["source"]["tag"],
                item["source"]["name"]
            )
            destination = DataPoint(
                item["destination"]["protocol"],
                item["destination"]["tag"],
                item["destination"]["name"]
            )
            self.mappings.append({
                "source": source,
                "destination": destination,
                "enabled": item["enabled"],
                "transformation": item["transformation"]
            })
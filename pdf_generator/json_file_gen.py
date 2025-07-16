import json

def make_file(output_obj):
    output_data = json.dumps(output_obj)
    with open("input.json", "w") as file:
        file.write(output_data)

import json

def make_file(output_obj,output_file="input.json"):
    output_data = json.dumps(output_obj)
    with open(output_file, "w") as file:
        file.write(output_data)

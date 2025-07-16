from json_file_gen import make_file
from pre_processing import categorize_products_with_cohere, refine_product_json


def generate_json(results,output_file="output.json"):
    products = ""
    filetered_list = {}
    for i in range(0,len(results)):
        products=products + str(i+1) + "." + results[i]["product name"] + ","
        filetered_list[results[i]["product name"]] = results[i]["description"]
    catogories = categorize_products_with_cohere(products)
    json_output = []
    for k in list(catogories):
        json_output.append({"category name": k ,"products":[refine_product_json({"product name":i,"description":filetered_list[i]}) for i in catogories[k]]})
    make_file(json_output,output_file)
import ollama
import os

model = "llama3.2"

#Paths to input and output files
input_file = "./data/grocery_list.txt"
output_file = "./data/categorized_grocery_list.txt"

#Check if the input file exists
if not os.path.exists(input_file):
    print(f"Input file '{input_file}' not found.")
    exit(1)

#Read the uncategorized grocery items from the input file
with open(input_file, "r") as f:
    items = f.read().strip()

items_list = items.splitlines()
formatter_items="\n".join(f"-{item.strip()}" for item in items_list)
#Prepare the prompt for the model
prompt = f"""
You are an assistant that catergorizes and sorts grocery items.

Here is a list of grocery items:

{formatter_items}

Please:
1. Categorize these items into appropriate Categories such as Produce, Dairy, Meat, Bakery, Beverages, etc.
2. Sort the items alphabetically within each category.
3. Present the categorized list in a clear and organized manner, using bullet points or numbering
4. Include every item without omission
"""
#Send the prompt and get the response
try:
    response = ollama.generate(model=model, prompt=prompt,options = {"max_tokens": 4096,"num_ctx": 4096})
    generated_text = response.get("response", "")
    print("==== Categorized List: ====\n")
    print(generated_text) 

    #Write the categorized list to the output file
    with open(output_file, "w") as f:
        f.write(generated_text.strip())

    print(f"Categorized Grocery lists has been saved to the {output_file}")
except Exception as e:
    print("An error occured:",str(e))


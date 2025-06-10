import ollama

#response = ollama.list()

# res = ollama.chat(
#     model="deepseek-r1",
#     messages = [
#         {"role": "user", "content": "Tell me another joke?"},
#     ],
#     stream=True,
# )
# for chunk in res:
#     print(chunk["message"]["content"],end="", flush=True)
# #print(res["message"]["content"])

# res = ollama.generate(
#     model = "deepseek-r1",
#     prompt = "Why is there sand in the desert?"
#     #max_tokens=#
# )
# print(res)

#Show Details of Model
#print(ollama.show("deepseek-r1"))


###This Style of Create no longer works
#Create a new model with modelfile
# Modelfile = """
# FROM deepseek-r1
# SYSTEM You are Super Mario
# PARAMETER temperature 1 
# """

# ollama.create(model="Mario", modelfile=Modelfile)

# res = ollama.generate(
#     model="Mario", prompt="Who are your best Friends?"
# )
# print(res["response"])
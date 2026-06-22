import google.generativeai as genai

genai.configure(api_key="AIzaSyDIMDdbVm0h4nMEL-nUwzgnPb1UdFKgNNU")

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
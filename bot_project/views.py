from django.shortcuts import render
from usiu_app.load_model_files import start_training


def home(request):
    return render(request, 'index.html')

def train_model(request, option=""):
    if option=="start":  
        start_training()
        return render(request, 'train.html', {'status': "Model trained!!!!!!"})
    else:
        return render(request, 'train.html', {'status': "Nothing happening!"})
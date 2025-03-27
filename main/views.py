import os
from django.shortcuts import render
from .forms import UploadFileForm
from sklearn.feature_extraction.text import TfidfVectorizer


# def process_file(file):
#     text = file.read().decode("utf-8")
#     words = text.split()  
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
#     tfidf_scores = dict(zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0]))
    
#     sorted_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:50]
#     return sorted_tfidf



# def upload_file(request):
#     if request.method == "POST":
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES["file"]
#             result = process_file(file)
#             return render(request, "result.html", {"result": result})
#     else:
#         form = UploadFileForm()
#     return render(request, "upload.html", {"form": form})

import chardet

def process_file(file_field):
    # Определяем кодировку файла
    with open(file_field.path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result["encoding"] if result["encoding"] else "utf-8"

    # Открываем файл с найденной кодировкой
    with open(file_field.path, "r", encoding=encoding, errors="ignore") as f:
        text = f.read()

    words = text.split()
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
    tfidf_scores = dict(zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0]))

    sorted_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:50]
    return sorted_tfidf



def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()  # Сохраняем файл в базе данных
            result = process_file(uploaded_file.file)  # Обрабатываем файл
            return render(request, "result.html", {"result": result})
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})

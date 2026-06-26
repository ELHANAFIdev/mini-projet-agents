# 1. N-khdmo b image Python khfifa bach l-app t-koun srii3a
FROM python:3.11-slim

# 2. N-7ddo l-dossier dyal l-khadma dakhil l-container
WORKDIR /app

# 3. N-copio l-fichie dyal requirements hwa l-auwel
COPY requirements.txt .

# 4. N-stalliw l-libraries (bla ma n-khliw l-cache bach t-b9a l-image sghira)
RUN pip install --no-cache-dir -r requirements.txt

# 5. N-copio l-code dyal l-proje kamel (l-dossier src, w l-files l-khrin)
COPY . .

# 6. N-7llo l-Port 8080 li gha-t-khdem fih l-app
EXPOSE 8080

# 7. L-command li gha-t-lansi FastAPI mlli i-ch3al l-container
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
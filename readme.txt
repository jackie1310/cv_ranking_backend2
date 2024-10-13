 
 khoi tao : python -m venv
 
 venv/Scripts/activate

for CMD: .\venv\Scripts\activate

pip install -r requirements.txt

CI/CD: cd C:/IIS/cv_ranking  && .\venv\Scripts\activate && pip install -r requirements.txt
 
 uvicorn main:app --port 8081
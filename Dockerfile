FROM python:3.9

WORKDIR /user/src/app

RUN pip install fastapi uvicorn[standard] gunicorn motor python-jose[cryptography] passlib python-multipart fpdf


COPY . .

CMD ["gunicorn", "main:app", "-w", "4", "-k" ,"uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]


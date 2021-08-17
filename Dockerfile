FROM python:3.9

WORKDIR /user/src/app


COPY . .

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD ["gunicorn", "main:app", "-w", "4", "-k" ,"uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]


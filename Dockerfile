FROM python:3.9.9

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

ENV ENVIRONMENT=DEV

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

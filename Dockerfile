FROM python:3.10.0a4-alpine
ADD . /code
WORKDIR /code
RUN pip install flask redis
EXPOSE 5000
CMD ["python", "flask_app.py"]

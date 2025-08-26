FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install Flask
CMD ["flask", "run", "--host=0.0.0.0"]

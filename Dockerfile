FROM python:3.13

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install ffmpeg -y

WORKDIR .
COPY . .
RUN ls -l
RUN cat cookies.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]

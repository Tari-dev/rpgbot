FROM python:3.10

ADD / /bot/

WORKDIR /bot

RUN apt-get update && apt-get upgrade -y

RUN python3 -m venv venv

ENV PATH="venv/bin:$PATH"

RUN pip install -U pip

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD ["bot.py"]

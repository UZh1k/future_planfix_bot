FROM python:latest

WORKDIR /usr/src/app

COPY ./ .
RUN pip3 install -r requirements.txt


ENTRYPOINT ["python"]

CMD ["bot.py"]
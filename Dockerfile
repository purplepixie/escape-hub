FROM python

WORKDIR /escapehub
COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD [ "sanic", "--host=0.0.0.0", "escape-hub", "--debug" ]
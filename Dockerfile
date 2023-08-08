FROM python

WORKDIR /escapehub
COPY . .
COPY example-config/rooms.json config/rooms.json
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD [ "sanic", "--host=0.0.0.0", "escape-hub", "--debug" ]
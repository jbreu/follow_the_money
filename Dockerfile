FROM python:3.13.2-bookworm

WORKDIR /python-docker

COPY . .

RUN apt install libxml2-dev libxslt-dev
RUN python3 -m pip install -r requirements.txt
RUN ls
RUN chmod u+x retrieve_data.sh && ./retrieve_data.sh

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]
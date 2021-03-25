FROM python

RUN mkdir app

# install python dependancies
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# install ogr2ogr
RUN apt-get update
RUN apt-get install -y gdal-bin

# get the scripts
COPY make_paths.py /app/
COPY process_buildings.py /app/
COPY process.sh /app/

# work it
WORKDIR /app
CMD [ "bash", "/app/process.sh" ]
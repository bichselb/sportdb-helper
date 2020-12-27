FROM python:3.8

RUN pip3 install \
	selenium==3.141.0 \
	pandas==1.1.5 \
	xlrd==2.0.1

WORKDIR "/sportdb-helper"
COPY . .

ENTRYPOINT ["python3", "./code/insert_data.py"]
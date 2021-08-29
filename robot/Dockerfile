FROM python:3.8-slim

WORKDIR /app

COPY ./ ./

RUN pip install requests
RUN pip3 install requests
RUN pip3 install loguru==0.5.3
RUN pip3 install is-msgs==1.1.15
RUN pip3 install is-wire==1.2.0
RUN pip3 install vine==1.3.0
RUN pip3 install --upgrade protobuf

ENTRYPOINT ["python3"]
CMD ["./src/robot.py"]
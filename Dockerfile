FROM python:3.8-slim-buster
 
WORKDIR /TicketIntegration
COPY . /TicketIntegration
 
RUN pip install -r requirements.txt
 
ENTRYPOINT ["python"]
CMD ["TicketIntegration.py"]
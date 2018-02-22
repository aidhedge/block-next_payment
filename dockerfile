# block-next_payment
FROM python:3
EXPOSE 7010
ENV FLASK_DEBUG=1
ENV PORT=7010
RUN pip install flask
RUN pip install cerberus
RUN pip install requests


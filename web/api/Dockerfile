FROM python:3.6

# Create the user that will run the app
RUN adduser --disabled-password --gecos '' api-user

ENV FLASK_APP=app.py

# Install requirements
ADD pacsltk /opt/pacsltk/
ADD src/requirements.txt /opt/requirements.txt
RUN pip install --upgrade pip
RUN pip install /opt/pacsltk
RUN pip install -r /opt/requirements.txt

ADD src /opt/perf_model_api/

WORKDIR /opt/perf_model_api
RUN chmod +x /opt/perf_model_api/run.sh
RUN chown -R api-user:api-user ./

USER api-user

EXPOSE 5000

CMD ["bash", "./run.sh"]

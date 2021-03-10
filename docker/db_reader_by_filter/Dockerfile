# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
ADD ./docker/db_reader_by_filter/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD ./source_code/db_reader_by_filter.py /app/
COPY ./source_code/pyTools /app/pyTools
ADD ./source_code/__init__.py /app/

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "db_reader_by_filter.py"]

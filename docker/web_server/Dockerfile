# keep our base image as small as possible
FROM nginx/unit

# same as "working_directory" in config.json
ADD ./source_code/web_server.py /app/
COPY ./source_code/pyTools /app/pyTools
ADD ./source_code/__init__.py /app/

# Install pip requirements
ADD ./docker/web_server/requirements.txt /



# add NGINX Unit and Node.js repos
RUN apt update                                                             \
    && apt install -y apt-transport-https gnupg1                           \
    && curl https://nginx.org/keys/nginx_signing.key | apt-key add -       \
    && echo "deb https://packages.nginx.org/unit/debian/ stretch unit"     \
         > /etc/apt/sources.list.d/unit.list                               \
    && echo "deb-src https://packages.nginx.org/unit/debian/ stretch unit" \
         >> /etc/apt/sources.list.d/unit.list                              \
    && curl https://deb.nodesource.com/setup_12.x | bash -                 
# install build chain
RUN apt update                                                          \
# add python dependencies
    &&  apt install -y python3-pip                                         \
# add app dependencies locally
    && python3 -m pip install virtualenv                                   \
    && apt-get -y install python3-venv                                     
RUN cd /app/ && python3 -m venv venv                                    \
    && /app/venv/bin/python3 -m pip install -r /requirements.txt            
# final cleanup
RUN apt autoremove --purge -y                                           \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

# port used by the listener in config.json
EXPOSE 80
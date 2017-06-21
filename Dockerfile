FROM debian
RUN apt-get update; apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
ADD requirements.txt /
RUN pip3 install -r requirements.txt
RUN rm ./requirements.txt
ADD photogen.py /app/
RUN chmod +x /app/photogen.py
VOLUME /workdir
ENV LC_CTYPE C.UTF-8

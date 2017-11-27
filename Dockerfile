FROM python:latest
ADD . /Discord-Selfbot

RUN cd Discord-Selfbot && \
    pip install -r requirements.txt

CMD ["/Discord-Selfbot/run_linuxmac.sh"]

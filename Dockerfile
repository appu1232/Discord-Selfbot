FROM python:latest

RUN git clone https://github.com/appu1232/Discord-Selfbot && \
    cd Discord-Selfbot && \
    pip install -r requirements.txt

CMD ["/Discord-Selfbot/run_linuxmac.sh"]

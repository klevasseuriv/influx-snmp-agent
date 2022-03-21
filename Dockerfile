FROM fedora:35

ADD ./dist/*.whl .

RUN dnf install -y net-snmp net-snmp-devel python3-net-snmp python3-devel

RUN python3 -m ensurepip && \
    python3 -m pip install *.whl

ENTRYPOINT ["influx-snmp-agent"]
CMD []

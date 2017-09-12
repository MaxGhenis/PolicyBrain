FROM ubuntu:15.04

RUN adduser ubuntu
RUN adduser ubuntu sudo
RUN echo "ubuntu:ubuntu" | chpasswd

RUN apt-get update && apt-get -yq install openssh-server \
    sudo \
    software-properties-common \
    python-software-properties

RUN mkdir -p /var/run/sshd
RUN mkdir /home/ubuntu/.ssh && chmod 700 /home/ubuntu/.ssh
RUN touch /home/ubuntu/.ssh/authorized_keys

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

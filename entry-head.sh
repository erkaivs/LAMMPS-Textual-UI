#!/bin/bash

if [[ ! -z $LMPUSER ]]; then
        (id $LMPUSER>/dev/null 2>&1) || useradd $LMPUSER -m -s /bin/bash
        (grep -q $LMPUSER /etc/sudoers) || (echo "$LMPUSER ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers)
        echo '[[ -z $SUDO_USER ]] && exec runuser -l $LMPUSER' > /root/.bashrc
        runuser -u $LMPUSER -- ssh-keygen -t ed25519 -N "" -f /home/$LMPUSER/.ssh/id_ed25519 -q
        runuser -u $LMPUSER -- cp /home/$LMPUSER/.ssh/id_ed25519.pub /home/$LMPUSER/.ssh/authorized_keys
        runuser -u $LMPUSER -- mkdir /home/$LMPUSER/venv
        runuser -u $LMPUSER -- python3 -m venv /home/$LMPUSER/venv
        runuser -u $LMPUSER -- /home/$LMPUSER/venv/bin/pip install --no-cache-dir textual numpy matplotlib
fi

echo Booting head node: ghead
service dbus start
service ssh start
service munge start

mkdir -p /home/share/bin
mkdir -p /home/share/files
cp /opt/bin/lmp_mpi /home/share/bin/
chmod +x /home/share/bin/lmp_mpi
chown -R 1000:1000 /home/share
cp -a /opt/potentials /home/share/files/

if [[ -z $NOSLURM ]]; then
        slurmctld -D
else
        while true; do
                sleep 10
        done
fi

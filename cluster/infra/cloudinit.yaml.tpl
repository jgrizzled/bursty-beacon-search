#cloud-config

users:
  - name: admin
    primary_group: admin
    groups: [adm, sudo]
    shell: /bin/bash
    lock_passwd: true
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ${ssh_public_key}

package_update: true
package_upgrade: true
packages:
  - ufw
  - curl
  - git
  - gcc
  - tar
  - tmux
  - htop

write_files:
  - path: /etc/ssh/sshd_config.d/cloudinit.conf
    content: |
      Port ${ssh_port}
      PasswordAuthentication no
      PermitRootLogin no
      X11Forwarding no
      MaxAuthTries 10
      AllowTcpForwarding yes
      AllowAgentForwarding yes

timezone: ${tz}

runcmd:
  - [systemctl, daemon-reload]
  - [systemctl, restart, ssh]

  - [ufw, default, deny, incoming]
  - [ufw, default, allow, outgoing]
  # Allow local incoming connections
  - [ufw, allow, from, 10.0.0.0/24]
  # Plain allow, NOT `ufw limit`: the orchestrator's setup sequence opens
  # ~6 ssh connections in a few seconds, and ufw's limit rule REJECTs the
  # 6th new connection per 30 s per source (= the whole fleet fails its
  # validation gate with "Connection refused"). Source filtering already
  # happens in the Hetzner cloud firewall (ssh_allowed_ips).
  - [ufw, allow, "${ssh_port}/tcp", comment, "SSH"]
  - [ufw, --force, enable]

  # Bounds the amount of logs that can survive on the system
  - [
      sed,
      "-i",
      "s/#SystemMaxUse=/SystemMaxUse=3G/g",
      /etc/systemd/journald.conf,
    ]
  - [
      sed,
      "-i",
      "s/#MaxRetentionSec=/MaxRetentionSec=1week/g",
      /etc/systemd/journald.conf,
    ]

  # Install uv for the admin user
  - [sudo, -u, admin, sh, -c, "curl -LsSf https://astral.sh/uv/install.sh | sh"]

  # github.com host key so the first ssh clone is non-interactive
  - [
      sudo,
      -u,
      admin,
      sh,
      -c,
      "mkdir -p ~/.ssh && chmod 700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null",
    ]

#!/bin/bash

function confirm_step {
    read -p "$1 (yes/no): " response
    if [ "$response" != "yes" ]; then
        echo "Operation cancelled."
        exit 1
    fi
}

# Enumerate current system status
confirm_step "Enumerate current system status?"
echo "System Info:"
uname -a
cat /etc/os-release
dpkg -l
rpm -qa
ps aux
netstat -tuln
iptables -L
ss -tuln
df -h
lsblk
cat /etc/passwd
cat /etc/group
crontab -l
# List of non-default packages
echo "Non-default packages:"
comm -23 <(sort <(dpkg-query -f '${binary:Package}\n' -W | sort)) <(sort /var/lib/dpkg/info/*list)

# Initial Hardening
confirm_step "Perform initial hardening?"
echo "Setting basic security policies..."
# Add your security policy settings here, e.g., password policies, account lockout policies

# Change all user passwords
read -p "Do you want to set a single password for all users? (yes/no): " singlePassword
if [ "$singlePassword" == "yes" ]; then
    read -s -p "Enter new password for all users: " newPassword
    echo
    for user in $(awk -F: '{ print $1}' /etc/passwd); do
        echo "$newPassword" | passwd --stdin $user
        chage -d 0 $user
    done
else
    for user in $(awk -F: '{ print $1}' /etc/passwd); do
        read -s -p "Enter new password for user $user: " newPassword
        echo
        echo "$newPassword" | passwd --stdin $user
        chage -d 0 $user
    done
fi

# Review and manage user accounts
confirm_step "Review and manage user accounts?"
for user in $(awk -F: '{ print $1}' /etc/passwd); do
    echo "Account: $user"
    id $user
    passwd -S $user
    echo "Choose action (delete, lock, unlock, addAdmin, removeAdmin, changeGroup, skip):"
    read action
    case $action in
        delete) userdel $user ;;
        lock) passwd -l $user ;;
        unlock) passwd -u $user ;;
        addAdmin) usermod -aG sudo $user ;;
        removeAdmin) gpasswd -d $user sudo ;;
        changeGroup)
            read -p "Enter new group for user $user: " newGroup
            usermod -G $newGroup $user
            ;;
    esac
done

# Flag open ports and firewall exclusions
confirm_step "Flag open ports and firewall exclusions?"
netstat -tuln
iptables -L

# Baseline operation
confirm_step "Perform baseline operation?"
echo "Checking system integrity..."
if [ -f /etc/debian_version ]; then
    debsums -c
elif [ -f /etc/redhat-release ]; then
    rpm -Va
fi

# Additional baseline checks
ps -eo pid,comm,lstart,etime | grep -vE "^\s*PID"
journalctl -xe --no-pager -n 20

# Update system and apps
confirm_step "Update system and apps?"
if [ -f /etc/debian_version ]; then
    apt update && apt upgrade -y
elif [ -f /etc/redhat-release ]; then
    dnf update -y
fi

# Update browsers and other common software
for app in $(dpkg -l | awk '/ii/{print $2}'); do
    if [[ $app =~ (chrome|firefox|edge) ]]; then
        echo "Updating $app..."
        apt-get install --only-upgrade $app
    else
        echo "Update $app? (yes/no):"
        read update
        if [ "$update" == "yes" ]; then
            apt-get install --only-upgrade $app
        fi
    done

import os
import subprocess
import platform
import getpass

def confirm_step(message):
    response = input(f"{message} (yes/no): ").lower()
    if response != 'yes':
        print("Operation cancelled.")
        exit(1)

def enumerate_system():
    confirm_step("Enumerate current system status?")
    print("System Info:")
    print(platform.uname())
    if os.name == 'nt':
        print(subprocess.check_output(['systeminfo']).decode())
        print(subprocess.check_output(['wmic', 'product', 'get', 'name']).decode())
        print(subprocess.check_output(['net', 'localgroup']).decode())
        print(subprocess.check_output(['schtasks', '/query']).decode())
    else:
        print(subprocess.check_output(['uname', '-a']).decode())
        print(subprocess.check_output(['cat', '/etc/os-release']).decode())
        print(subprocess.check_output(['dpkg', '-l']).decode())
        print(subprocess.check_output(['rpm', '-qa']).decode())
        print(subprocess.check_output(['ps', 'aux']).decode())
        print(subprocess.check_output(['netstat', '-tuln']).decode())
        print(subprocess.check_output(['iptables', '-L']).decode())
        print(subprocess.check_output(['ss', '-tuln']).decode())
        print(subprocess.check_output(['df', '-h']).decode())
        print(subprocess.check_output(['lsblk']).decode())
        print(subprocess.check_output(['cat', '/etc/passwd']).decode())
        print(subprocess.check_output(['cat', '/etc/group']).decode())
        print(subprocess.check_output(['crontab', '-l']).decode())

def change_passwords():
    confirm_step("Change user passwords?")
    single_password = input("Do you want to set a single password for all users? (yes/no): ").lower() == 'yes'
    if single_password:
        new_password = getpass.getpass("Enter new password for all users: ")
    if os.name == 'nt':
        users = subprocess.check_output(['net', 'user']).decode().splitlines()
        users = [user.strip() for user in users if user.strip() and not user.startswith('---')]
        for user in users:
            if not single_password:
                new_password = getpass.getpass(f"Enter new password for user {user}: ")
            subprocess.run(['net', 'user', user, new_password])
    else:
        with open('/etc/passwd') as f:
            users = [line.split(':')[0] for line in f.readlines()]
        for user in users:
            if not single_password:
                new_password = getpass.getpass(f"Enter new password for user {user}: ")
            subprocess.run(['passwd', user], input=new_password, encoding='ascii')

def manage_users():
    confirm_step("Review and manage user accounts?")
    if os.name == 'nt':
        users = subprocess.check_output(['net', 'user']).decode().splitlines()
        users = [user.strip() for user in users if user.strip() and not user.startswith('---')]
        groups = subprocess.check_output(['net', 'localgroup']).decode().splitlines()
        groups = [group.strip() for group in groups if group.strip()]
    else:
        users = [line.split(':')[0] for line in open('/etc/passwd').readlines()]
        groups = [line.split(':')[0] for line in open('/etc/group').readlines()]
    
    for user in users:
        print(f"Account: {user}")
        if os.name == 'nt':
            print(subprocess.check_output(['net', 'user', user]).decode())
        else:
            print(subprocess.check_output(['id', user]).decode())
            print(subprocess.check_output(['passwd', '-S', user]).decode())
        action = input("Choose action (delete, lock, unlock, addAdmin, removeAdmin, changeGroup, skip): ").strip().lower()
        if action == 'delete':
            if os.name == 'nt':
                subprocess.run(['net', 'user', user, '/delete'])
            else:
                subprocess.run(['userdel', user])
        elif action == 'lock':
            if os.name == 'nt':
                subprocess.run(['net', 'user', user, '/active:no'])
            else:
                subprocess.run(['passwd', '-l', user])
        elif action == 'unlock':
            if os.name == 'nt':
                subprocess.run(['net', 'user', user, '/active:yes'])
            else:
                subprocess.run(['passwd', '-u', user])
        elif action == 'addadmin':
            if os.name == 'nt':
                subprocess.run(['net', 'localgroup', 'Administrators', user, '/add'])
            else:
                subprocess.run(['usermod', '-aG', 'sudo', user])
        elif action == 'removeadmin':
            if os.name == 'nt':
                subprocess.run(['net', 'localgroup', 'Administrators', user, '/delete'])
            else:
                subprocess.run(['gpasswd', '-d', user, 'sudo'])
        elif action == 'changegroup':
            new_group = input(f"Enter new group for user {user}: ").strip()
            if os.name == 'nt':
                subprocess.run(['net', 'localgroup', new_group, user, '/add'])
            else:
                subprocess.run(['usermod', '-G', new_group, user])

def update_system():
    confirm_step("Update system and apps?")
    if os.name == 'nt':
        subprocess.run(['powershell', 'Install-WindowsUpdate', '-AcceptAll', '-AutoReboot'])
    else:
        if os.path.exists('/etc/debian_version'):
            subprocess.run(['apt', 'update'])
            subprocess.run(['apt', 'upgrade', '-y'])
        elif os.path.exists('/etc/redhat-release'):
            subprocess.run(['dnf', 'update', '-y'])

def main():
    enumerate_system()
    change_passwords()
    manage_users()
    update_system()

if __name__ == "__main__":
    main()

function Confirm-Step($message) {
    $response = Read-Host -Prompt "$message (yes/no)"
    if ($response -ne "yes") {
        Write-Host "Operation cancelled."
        exit
    }
}

# Enumerate current system status
Confirm-Step "Enumerate current system status?"
Get-ComputerInfo
Get-WmiObject -Class Win32_Product
Get-Service | Where-Object { $_.StartType -eq 'Automatic' }
Get-NetTCPConnection -State Listen
Get-NetFirewallRule -Enabled True
Get-SmbShare
Get-LocalUser
Get-LocalGroup
Get-ScheduledTask | Where-Object { $_.State -eq 'Ready' }
# List of non-default packages
Get-InstalledModule

# Initial Hardening
Confirm-Step "Perform initial hardening?"
Write-Host "Setting basic security policies..."
Set-ExecutionPolicy RemoteSigned
# Add your security policy settings here, e.g., password policies, account lockout policies

# Change all user passwords
$singlePassword = Read-Host -Prompt "Do you want to set a single password for all users? (yes/no)"
if ($singlePassword -eq 'yes') {
    $newPassword = Read-Host -Prompt "Enter new password for all users"
    Get-LocalUser | ForEach-Object {
        $_ | Set-LocalUser -Password (ConvertTo-SecureString -AsPlainText $newPassword -Force)
        $_ | Set-LocalUser -PasswordNeverExpires $false
    }
} else {
    Get-LocalUser | ForEach-Object {
        $newPassword = Read-Host -Prompt "Enter new password for user $_"
        $_ | Set-LocalUser -Password (ConvertTo-SecureString -AsPlainText $newPassword -Force)
        $_ | Set-LocalUser -PasswordNeverExpires $false
    }
}

# Review and manage user accounts
Confirm-Step "Review and manage user accounts?"
Get-LocalUser | ForEach-Object {
    Write-Host "Account: $_"
    Write-Host "Admin: $($_.PrincipalSource -eq 'Local')"
    Write-Host "Locked: $($_.AccountLockedOut)"
    Write-Host "Group Memberships: $(Get-LocalGroupMember -Member $_)"
    $action = Read-Host -Prompt "Choose action (delete, lock, unlock, addAdmin, removeAdmin, changeGroup, skip)"
    switch ($action) {
        'delete' { Remove-LocalUser -Name $_ }
        'lock' { $_ | Disable-LocalUser }
        'unlock' { $_ | Enable-LocalUser }
        'addAdmin' { Add-LocalGroupMember -Group 'Administrators' -Member $_ }
        'removeAdmin' { Remove-LocalGroupMember -Group 'Administrators' -Member $_ }
        'changeGroup' {
            $newGroup = Read-Host -Prompt "Enter new group for user $_"
            Remove-LocalGroupMember -Group $(Get-LocalGroupMember -Member $_) -Member $_
            Add-LocalGroupMember -Group $newGroup -Member $_
        }
    }
}

# Flag open ports and firewall exclusions
Confirm-Step "Flag open ports and firewall exclusions?"
Get-NetTCPConnection -State Listen | Format-Table
Get-NetFirewallRule -Enabled True | Format-Table

# Baseline operation
Confirm-Step "Perform baseline operation?"
sfc /scannow
DISM /Online /Cleanup-Image /RestoreHealth

# Additional baseline checks
Get-Process | Where-Object { $_.StartTime -gt (Get-Date).AddMinutes(-5) } | Format-Table
Get-WinEvent -LogName Security -MaxEvents 20 | Format-Table

# Update system and apps
Confirm-Step "Update system and apps?"
Install-WindowsUpdate -AcceptAll -AutoReboot
Get-InstalledModule -Name PSWindowsUpdate -Force | Update-Module
Get-InstalledModule -Name PackageManagement -Force | Update-Module

# Update browsers and other common software
$software = Get-WmiObject -Class Win32_Product
foreach ($app in $software) {
    if ($app.Name -match 'Chrome|Firefox|Edge') {
        Start-Process -FilePath $app.InstallLocation -ArgumentList "--silent --update"
    } else {
        $update = Read-Host -Prompt "Update $($app.Name)? (yes/no)"
        if ($update -eq 'yes') {
            # Add your software update logic here
        }
    }
}

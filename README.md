# PySQLBackup

This project is made to allow you create Sql Server backups.

It is required to be executed as administrator to full secure the access of writing to the backups directory, otherwise it can not work properly.

It has to be executed in the machine where the sql server service is installed or a machine with the correct tools installed and access to the correct directories (sqlcmd.exe required).

This program uses the GlamMonitor logging package which allows you to store logs locally and monitor the process from the GlamMonitorAPI (configuration required).

## Configuration
To execute the program you will need to configure the following environment variables:

PYTHONUNBUFFERED=1  
DATABASE_INSTANCE={server_name\instance_name}   
DATABASE_LIST={comma separated list of databases to backup} 
DATABASE_USER={username}    
DATABASE_PWD={password}     
PATH_BACKUP={local path to the backups directory}   
N_COPIES={number of copies to keep} 

> If you want to copy the backups to a network directory, you must add also the following variables 

NETWORK_PATH={network path to the main directory}   
NETWORK_PATH_VOLUME={name assigned to the network path when it is mounted}  
NETWORK_USER={network directory credentials user}   
NETWORK_PWD={network directory credentials password}    
NETWORK_MIRROR_RELATIVE_PATH={relative path to concatenate to the network_path_volume where the backups will be copied} 

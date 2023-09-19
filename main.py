import datetime
import os
import subprocess
import py7zr
from GlamMonitor import Monitor


def execute_backup():
    monitor = Monitor.Monitor()
    # Define global variables
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    current_time = datetime.datetime.now().strftime("%H%M%S")
    current_datetime = current_date + "." + current_time

    # Define local variables
    destination_backup_folder = os.environ['PATH_BACKUP']
    number_of_copies = int(os.environ['N_COPIES'])

    # Initialize log file
    monitor.info(f'Backup started at {current_datetime}')

    database_list = os.environ['DATABASE_LIST']
    database_instance = os.environ['DATABASE_INSTANCE']
    database_user = os.environ['DATABASE_USER']
    database_pwd = os.environ['DATABASE_PWD']

    # Create backup of SQL Server database
    for database_name in database_list.split(","):
        try:
            # Create backup file
            monitor.info(f'Processing backup of {database_name}')
            subprocess.run(["sqlcmd", "-S", database_instance, "-U", database_user, "-P", database_pwd, "-Q",
                            f"BACKUP DATABASE {database_name} "
                            f"TO DISK = '{destination_backup_folder}\\{current_datetime}.{database_name}.bak' "
                            f"WITH DESCRIPTION = 'Backup {database_name}', INIT;"],
                           capture_output=True, text=True, check=True)

            # Compress backup file
            monitor.info(f'Compressing backup of {database_name}')
            with py7zr.SevenZipFile(f"{destination_backup_folder}\\{current_datetime}.{database_name}.7z",
                                    'w') as archive:
                archive.writeall(f"{destination_backup_folder}\\{current_datetime}.{database_name}.bak",
                                 'base')

            # Delete backup file
            monitor.info(f'Removing backup file of {database_name}')
            os.remove(f"{destination_backup_folder}\\{current_datetime}.{database_name}.bak")

            # Delete old backup files
            if number_of_copies > 0:
                monitor.info(f'Removing old copies of {database_name} backups')
                backup_files = [f for f in os.listdir(destination_backup_folder) if f.endswith(f'.{database_name}.7z')]
                backup_files.sort(reverse=True)

                for old_backup in backup_files[number_of_copies:]:
                    old_backup_path = os.path.join(destination_backup_folder, old_backup)
                    os.remove(old_backup_path)

            monitor.info(f'Finished backup of {database_name}')
        except Exception as e:
            monitor.error(f'Error performing backup of {database_name}: {str(e)}')

    # Copy files to network directory
    try:
        monitor.info('Checking network path to mirror backups')
        if (os.environ.__contains__('NETWORK_PATH') and os.environ.__contains__('NETWORK_USER')
                and os.environ.__contains__('NETWORK_PWD') and os.environ.__contains__('NETWORK_MIRROR_RELATIVE_PATH')):
            network_path = os.environ['NETWORK_PATH']
            network_user = os.environ['NETWORK_USER']
            network_pwd = os.environ['NETWORK_PWD']
            mirror_folder = os.environ['NETWORK_MIRROR_RELATIVE_PATH']
            network_volume = 'X'
            if os.environ.__contains__('NETWORK_PATH_VOLUME') and len(os.environ['NETWORK_PATH_VOLUME']) == 1:
                network_volume = os.environ['NETWORK_PATH_VOLUME']

            monitor.info(f'Mount {network_path} as {network_volume}')
            command = f'net use {network_volume}: {network_path} /user:{network_user} {network_pwd}'
            subprocess.run(command, shell=True, check=False)

            if not os.path.exists(f"{network_volume}:\\{mirror_folder}"):
                monitor.info(f'Directory {network_volume}:\\{mirror_folder} not existing. Creating..')
                os.makedirs(f"{network_volume}:\\{mirror_folder}")

            monitor.info(f'Mirror backups directory to {network_volume}:\\{mirror_folder}')
            command = f'robocopy "{destination_backup_folder}" {network_volume}:\\{mirror_folder} /MIR'
            subprocess.run(command, shell=True, check=False)

            monitor.info('Check copied files')
            mirror_files = [f for f in os.listdir(destination_backup_folder) if f.endswith(f'.7z')]

            for local_backup in mirror_files:
                mirror_backup = os.path.join(f'{network_volume}:\\{mirror_folder}', local_backup)
                if not os.path.exists(mirror_backup):
                    monitor.error(f'Backup file {local_backup} does not exist')

            monitor.info(f'Unmount {network_volume}:')
            command = f'net use {network_volume}: /delete'
            subprocess.run(command, shell=True, check=False)
        else:
            monitor.info('Network  path not defined')
    except Exception as e:
        monitor.error(f'Error mirroring backups to network path: {str(e)}')

    monitor.close()


if __name__ == "__main__":
    execute_backup()

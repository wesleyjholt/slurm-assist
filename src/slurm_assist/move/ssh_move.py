import subprocess
import os
import tempfile

def single_run(
    id: int,
    data: list[str],
    results_dir: str,
    hostname: str,
    username: str,
    key_filename: str,
    remote_dir: str
):
    # Get the files to move
    local_path = data[0]
    
    # Compress and transfer the files to the remote server
    remote_paths = compress_and_transfer(hostname, username, key_filename, [local_path], remote_dir)
    remote_path = remote_paths[0]

    return remote_path


def compress_and_transfer(hostname, username, key_filename, local_paths, remote_dir, archive_name=None):
    # Use tempfile to create an archive name, if not provided
    if archive_name is None:
        tmp_basename = os.path.relpath(tempfile.NamedTemporaryFile(dir='.').name, '.')
        archive_name = tmp_basename + '.tar.gz'
    
    # Expand paths
    key_filename = os.path.expanduser(key_filename)
    
    # Create the tar command for the list of files
    compress_command = ["tar", "-czf", archive_name] + local_paths
    
    try:
        # Step 1: Compress the files into a tar.gz archive
        print(f"Compressing files into {archive_name}...")
        subprocess.run(compress_command, check=True)
        print(f"Compression successful: {archive_name}")

        # Step 2: Create the remote directory if it does not exist
        ssh_mkdir_command = f"mkdir -p {remote_dir}"
        ssh_mkdir = [
            "ssh",
            "-i", key_filename,
            f"{username}@{hostname}",
            ssh_mkdir_command
        ]
        print(f"Creating remote directory {remote_dir}...")
        subprocess.run(ssh_mkdir, check=True)
        print(f"Remote directory created: {remote_dir}")

        # Step 3: Transfer the compressed file to the remote server using scp
        scp_command = [
            "scp",
            "-i", key_filename,  # Path to SSH private key
            archive_name,        # Local compressed file
            f"{username}@{hostname}:{remote_dir}"  # Remote destination (user@host:/remote/path)
        ]
        print(f"Transferring {archive_name} to {remote_dir} on {hostname}...")
        subprocess.run(scp_command, check=True)
        print(f"Transfer successful.")

        # Step 4: Connect to the remote server to uncompress the archive
        uncompress_command = f"tar -xzf {remote_dir}/{archive_name} -C {remote_dir}"
        ssh_command = [
            "ssh",
            "-i", key_filename,  # Path to SSH private key
            f"{username}@{hostname}",  # Remote user and host
            uncompress_command  # Command to uncompress the file on remote server
        ]
        print(f"Uncompressing {archive_name} on remote server...")
        subprocess.run(ssh_command, check=True)
        print(f"Uncompression successful on {hostname}.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    finally:
        # Optionally, you can delete the local archive after transfer if no longer needed
        if os.path.exists(archive_name):
            os.remove(archive_name)
            print(f"Removed local archive {archive_name}.")
        # Delete the remote archive after uncompression
        ssh_delete_command = f"rm {remote_dir}/{archive_name}"
        ssh_delete = [
            "ssh",
            "-i", key_filename,
            f"{username}@{hostname}",
            ssh_delete_command
        ]
        print(f"Deleting remote archive {archive_name}...")
        subprocess.run(ssh_delete, check=True)
        print(f"Deleted remote archive {archive_name}.")
    
    remote_paths = [os.path.join(remote_dir, p) for p in local_paths]
    return remote_paths


# Example usage
if __name__ == "__main__":
    hostname = "your_remote_host"      # Replace with your remote host address
    username = "your_username"         # Replace with your SSH username
    key_filename = "~/.ssh/id_rsa"     # Path to your SSH private key (e.g., ~/.ssh/id_rsa)
    local_files = ["/path/to/file1", "/path/to/file2", "/path/to/file3"]  # List of files to compress
    remote_dir = "/path/to/remote_dir" # Replace with the remote directory path
    
    compress_and_transfer(hostname, username, key_filename, local_files, remote_dir)




# import subprocess
# import os

# def compress_and_transfer(hostname, username, key_filename, local_paths, remote_path, archive_name="archive.tar.gz"):
#     # Expand paths
#     key_filename = os.path.expanduser(key_filename)
#     local_dir = os.path.expanduser(local_dir)
    
#     # Compress the local directory into a tar.gz archive
#     archive_path = f"{local_dir}.tar.gz"
#     compress_command = ["tar", "-czf", archive_path, "-C", os.path.dirname(local_dir), os.path.basename(local_dir)]
    
#     try:
#         # Step 1: Compress the directory
#         print(f"Compressing {local_dir} into {archive_path}...")
#         subprocess.run(compress_command, check=True)
#         print(f"Compression successful: {archive_path}")

#         # Step 2: Transfer the compressed file to the remote server using scp
#         scp_command = [
#             "scp",
#             "-i", key_filename,  # Path to SSH private key
#             archive_path,        # Local compressed file
#             f"{username}@{hostname}:{remote_dir}"  # Remote destination (user@host:/remote/path)
#         ]
#         print(f"Transferring {archive_path} to {remote_dir} on {hostname}...")
#         subprocess.run(scp_command, check=True)
#         print(f"Transfer successful.")

#         # Step 3: Connect to the remote server to uncompress the archive
#         uncompress_command = f"tar -xzf {remote_dir}/{os.path.basename(archive_path)} -C {remote_dir}"
#         ssh_command = [
#             "ssh",
#             "-i", key_filename,  # Path to SSH private key
#             f"{username}@{hostname}",  # Remote user and host
#             uncompress_command  # Command to uncompress the file on remote server
#         ]
#         print(f"Uncompressing {archive_path} on remote server...")
#         subprocess.run(ssh_command, check=True)
#         print(f"Uncompression successful on {hostname}.")

#     except subprocess.CalledProcessError as e:
#         print(f"Error: {e}")
#     finally:
#         # Optionally, you can delete the local archive after transfer if no longer needed
#         if os.path.exists(archive_path):
#             os.remove(archive_path)
#             print(f"Removed local archive {archive_path}.")

# # Example usage
# if __name__ == "__main__":
#     hostname = "your_remote_host"      # Replace with your remote host address
#     username = "your_username"         # Replace with your SSH username
#     key_filename = "~/.ssh/id_rsa"     # Path to your SSH private key (e.g., ~/.ssh/id_rsa)
#     local_dir = "/path/to/local_dir"   # Replace with the local directory path
#     remote_dir = "/path/to/remote_dir" # Replace with the remote directory path
    
#     compress_and_transfer(hostname, username, key_filename, local_dir, remote_dir)



# import os
# from fabric import Connection
# from invoke import run as local

# def compress_and_transfer_to_remote(hostname, username, key_filename, local_dir, remote_dir):
#     # Expand paths
#     key_filename = os.path.expanduser(key_filename)
#     local_dir = os.path.expanduser(local_dir)
    
#     # Compress the local directory into a tar.gz archive
#     archive_name = os.path.basename(local_dir) + ".tar.gz"
#     archive_path = f"{local_dir}.tar.gz"
#     compress_command = f"tar -czf {archive_path} -C {os.path.dirname(local_dir)} {os.path.basename(local_dir)}"
    
#     try:
#         # Step 1: Compress the directory locally
#         print(f"Compressing {local_dir} into {archive_path}...")
#         local(compress_command, pty=True)
#         print(f"Compression successful: {archive_path}")

#         # Step 2: Establish SSH connection using Fabric
#         conn = Connection(host=hostname, user=username, connect_kwargs={"key_filename": key_filename})

#         # Step 3: Transfer the compressed file using Fabric's put method
#         print(f"Transferring {archive_path} to {remote_dir} on {hostname}...")
#         conn.put(archive_path, remote=remote_dir)
#         print(f"Transfer successful.")

#         # Step 4: Uncompress the file on the remote server
#         remote_archive_path = f"{remote_dir}/{archive_name}"
#         uncompress_command = f"tar -xzf {remote_archive_path} -C {remote_dir}"
#         print(f"Uncompressing {archive_name} on remote server...")
#         conn.run(uncompress_command)
#         print(f"Uncompression successful on {hostname}.")

#     except Exception as e:
#         print(f"Error: {str(e)}")

#     finally:
#         # Optionally, remove the local archive after transfer
#         if os.path.exists(archive_path):
#             os.remove(archive_path)
#             print(f"Removed local archive {archive_path}.")
#         # Close the connection
#         conn.close()

# # Example usage
# if __name__ == "__main__":
#     hostname = "your_remote_host"      # Replace with your remote host address
#     username = "your_username"         # Replace with your SSH username
#     key_filename = "~/.ssh/id_rsa"     # Path to your SSH private key (e.g., ~/.ssh/id_rsa)
#     local_dir = "/path/to/local_dir"   # Replace with the local directory path
#     remote_dir = "/path/to/remote_dir" # Replace with the remote directory path
    
#     compress_and_transfer_with_fabric(hostname, username, key_filename, local_dir, remote_dir)


# import os
# from fabric import Connection



# def move_dir_via_ssh_with_key(hostname, username, key_filename, local_path, remote_path):
#     key_filename = os.path.expanduser(key_filename)
#     local_path = os.path.expanduser(local_path)
#     # destination = os.path.expanduser(destination)

#     try:
#         conn = Connection(host=hostname, user=username, connect_kwargs={"key_filename": key_filename})
#         # result = conn.run(f"mv {source} {destination}", hide=True)
#         # result = conn.run(f"pwd", hide=True)
#         result = conn.put(local_path, remote=remote_path, recursive=True)

#         print(result.stdout)
#         if result.ok:
#             print(f"Successfully moved {local_path} to {remote_path}")
#         else:
#             print(f"Failed to move {local_path}")

#     except Exception as e:
#         print(f"Error: {str(e)}")

#     finally:
#         # Close the connection
#         conn.close()

# # Example usage
# if __name__ == "__main__":
#     hostname = "your_remote_host"  # Replace with your remote host address
#     username = "your_username"     # Replace with your SSH username
#     key_filename = "/path/to/your/private_key"  # Path to your SSH private key (e.g., ~/.ssh/id_rsa)
#     source_dir = "/path/to/source" # Replace with the source directory path
#     dest_dir = "/path/to/destination" # Replace with the destination directory path
#     files_to_move = ["file1.txt", "file2.txt"] # List of files to move

#     move_dir_via_ssh_with_key(hostname, username, key_filename, source_dir, dest_dir, files_to_move)

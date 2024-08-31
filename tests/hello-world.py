print('hello, world!')

from mpi4py import MPI

# # Initialize the MPI environment
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()  # Get the rank of the current process
# size = comm.Get_size()  # Get the total number of processes

# # Send a message from process 0 to process 1
# if rank == 0:
#     data = "Hello from process 0"
#     comm.send(data, dest=1, tag=11)
#     print(f"Process {rank} sent message: {data}")
# elif rank == 1:
#     data = comm.recv(source=0, tag=11)
#     print(f"Process {rank} received message: {data}")

# # Broadcast a message from process 0 to all other processes
# if rank == 0:
#     data = "Broadcast message from process 0"
# else:
#     data = None

# data = comm.bcast(data, root=0)
# print(f"Process {rank} received broadcast message: {data}")

# # Finalize the MPI environment (optional, handled automatically on exit)
# MPI.Finalize()

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Hello from rank {rank} out of {size} processes")

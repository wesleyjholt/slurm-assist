import sys
import jax
from jax import jit, vmap, jacobian
import numpyro
import numpyro.distributions as dist
import equinox as eqx

def do_jax_stuff():
    print('\n==============================')
    print('Python version:', sys.version)
    print('JAX version:', jax.__version__)
    print('Equinox version:', eqx.__version__)
    print('Numpyro version:', numpyro.__version__)
    print('==============================\n')

    ## Check for GPU devices
    try:
        jax.devices('gpu')
    except RuntimeError:
        gpu_devices = []
    else:
        gpu_devices = jax.devices('gpu')

    ## Check for CPU devices
    try:
        jax.devices('cpu')
    except RuntimeError:
        cpu_devices = []
    else:
        cpu_devices = jax.devices('cpu')

    print('Jax GPU devices:', gpu_devices)
    print('Jax CPU devices:', cpu_devices)

    key = jax.random.PRNGKey(0)
    key, subkey = jax.random.split(key, 2)

    ## Make a model (with Equinox)
    model = eqx.nn.MLP(
        in_size=1024,
        out_size=10,
        width_size=256,
        depth=10,
        activation=jax.nn.tanh,
        key=subkey,
    )

    ## Randomly sample the inputs (with Numpyro)
    num_samples = 100_000
    xs = dist.Uniform().sample(key, (num_samples, 1024))

    ## Evaluate output and Jacobian
    val = jit(vmap(model))(xs)
    jac = jit(vmap(jacobian(model)))(xs)

    print('\nFinished!')
    print('The shape of the output is', val.shape)
    print('The shape of the Jacobian is', jac.shape)

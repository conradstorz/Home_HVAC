"""retrieve environment variables even when running as a service and the variables for a logged-in
user are not loaded."""

from loguru import logger

@logger.catch
def retrieve_env_vars():
    import subprocess

    process = subprocess.Popen(['bash', '-c', 'source .bashrc && env'], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    logger.info(f'{output=}')

    env_vars = {}
    for line in output.decode().split('\n'):
        parts = line.split('=', 1)
        logger.info(f'{parts=}')
        if len(parts) == 2:
            env_vars[parts[0]] = parts[1]

    logger.info(env_vars)
    return env_vars


if __name__ == '__main__':
    retrieve_env_vars()
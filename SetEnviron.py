def environ(env_file=".env"):

    import os
    with open(env_file) as file:

        for line in file:

            if line.startswith('#') or not line.strip():
                continue

            key, value = line.strip().split('=', 1)
            os.environ[key] = value  # Load to local environ
            
        file.close()
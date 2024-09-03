from .utils import load_yaml, merge_dicts

class JobGroup(dict):
    def __init__(self, config):
        if isinstance(config, str):
            # Single file
            _config = load_yaml(config)
        elif isinstance(config, dict):
            # Single dictionary
            _config = config
        else:
            # List of files, dictionaries, or None values
            _configs = []
            for c in config:
                if isinstance(c, str):
                    _configs.append(load_yaml(c))
                elif isinstance(c, dict):
                    _configs.append(c)
                elif c is not None:
                    raise ValueError(f"Invalid config: {c}")
            if len(_configs) == 0:
                raise ValueError("No valid configs found.")
            _config = merge_dicts(*_configs)
        super().__init__(_config)
    
    def submit(self):
        raise NotImplementedError('submit method is not implemented. Implement me!')
    
    def cancel(self):
        raise NotImplementedError('cancel method is not implemented. Implement me!')

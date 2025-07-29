from pathlib import Path

class PathHelper:
    # Static property for project root
    _project_root = Path(__file__).parent.parent.parent

    @staticmethod
    def get_project_root():
        return PathHelper._project_root

    @staticmethod
    def get_config_dir():
        """Get the config directory path."""
        return PathHelper._project_root / 'app' / 'config'

    @staticmethod
    def get_model_dir():
        """Get the model directory path."""
        return PathHelper._project_root / 'app' / 'model'

    @staticmethod
    def get_data_dir():
        """Get the data directory path."""
        return PathHelper._project_root / 'data'

    @staticmethod
    def get_dataset_dir():
        """Get the dataset directory path."""
        return PathHelper._project_root / 'app' / 'dataset'

    @staticmethod
    def get_logs_dir():
        """Get the logs directory path."""
        return PathHelper._project_root / 'app' / 'logs'

    @staticmethod
    def get_config_file(filename: str):
        """Get a specific config file path."""
        return PathHelper.get_config_dir() / filename

    @staticmethod
    def get_model_file(filename: str):
        """Get a specific model file path."""
        return PathHelper.get_model_dir() / filename

    @staticmethod
    def get_data_file(filename: str):
        """Get a specific data file path."""
        return PathHelper.get_data_dir() / filename

    @staticmethod
    def ensure_dir_exists(path: Path):
        """Ensure a directory exists, create if it doesn't."""
        path.mkdir(parents=True, exist_ok=True)
        return path

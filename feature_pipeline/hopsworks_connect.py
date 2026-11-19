import hopsworks
import config


def connect():
    """Log in to Hopsworks and return the project and its feature store."""
    project = hopsworks.login(
        host=config.HOPSWORKS_HOST,
        project=config.HOPSWORKS_PROJECT,
        api_key_value=config.HOPSWORKS_API_KEY,
    )
    feature_store = project.get_feature_store()
    return project, feature_store


# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    project, fs = connect()
    print("Connected to project:", project.name)
    print("Feature store:", fs.name)
from sklearn.model_selection import GridSearchCV
from models.predictive_model import PredictiveModel
from utils.logger import setup_logger
import numpy as np

# Initialize logger
logger = setup_logger()

def optimize_hyperparams():
    """
    Optimize hyperparameters for the predictive model.
    """
    try:
        # Load data
        data = pd.read_csv("data/datasets/historical_data.csv")
        X = data.drop(columns=["target"])
        y = data["target"]

        # Define hyperparameter grid
        param_grid = {
            "filters": [32, 64, 128],
            "kernel_size": [3, 5],
            "lstm_units": [50, 100],
            "learning_rate": [0.001, 0.01]
        }

        # Initialize model
        model = PredictiveModel()

        # Perform grid search
        logger.info("Starting hyperparameter optimization...")
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            scoring="neg_mean_squared_error",
            cv=3,
            verbose=2
        )
        grid_search.fit(X, y)

        # Save best parameters
        best_params = grid_search.best_params_
        logger.info(f"Best hyperparameters: {best_params}")
        with open("config/model_config.yaml", "w") as f:
            yaml.dump(best_params, f)

    except Exception as e:
        logger.error(f"Error during hyperparameter optimization: {e}")

if __name__ == "__main__":
    optimize_hyperparams()
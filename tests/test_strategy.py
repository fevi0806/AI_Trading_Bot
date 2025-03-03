import unittest
from models.predictive_model import PredictiveModel
from data.data_preprocessor import DataPreprocessor

class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.data = pd.read_csv("data/datasets/historical_data.csv")
        self.preprocessor = DataPreprocessor()
        self.model = PredictiveModel()

    def test_predictive_model(self):
        """
        Test the predictive model's performance.
        """
        X, y = self.preprocessor.preprocess(self.data)
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        self.model.train(X_train, y_train)
        predictions = self.model.predict(X_test)

        self.assertGreater(len(predictions), 0, "Predictions should not be empty.")

if __name__ == "__main__":
    unittest.main()
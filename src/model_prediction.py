import argparse
import json
import os

import joblib
import pandas as pd
import torch

from config import (
    DATASET_PATH,
    MODELS_PATH,
)
from logger import get_logger

logger = get_logger()


def load_data(file_path):
    # Load test data from CSV file
    df = pd.read_csv(os.path.join(DATASET_PATH, file_path))
    return df


def load_model(model_path):
    # Load the trained model
    if model_path.endswith(".pkl"):
        model = joblib.load(os.path.join(MODELS_PATH, model_path))
    else:
        model = torch.load(os.path.join(MODELS_PATH, model_path))
    return model


def make_predictions(df, model):
    # Use the model to make predictions on the test data
    predictions = model.predict(df)
    return predictions


def save_predictions(predictions, predictions_file):
    # TODO:  Save predictions to a JSON file
    json_predictions = {"target": predictions}
    with open(predictions_file, "w") as f:
        json.dump(json_predictions, f)
    logger.info(f"Predictions saved to {predictions_file}")
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(description="Prediction script for Energy Forecasting Hackathon")
    parser.add_argument(
        "--input_file", type=str, default="data/test_data.csv", help="Path to the test data file to make predictions"
    )
    parser.add_argument("--model_file", type=str, default="models/model.pkl", help="Path to the trained model file")
    parser.add_argument(
        "--output_file", type=str, default="predictions/predictions.json", help="Path to save the predictions"
    )
    return parser.parse_args()


def main(input_file, model_file, output_file):
    df = load_data(input_file)
    model = load_model(model_file)
    predictions = make_predictions(df, model)
    save_predictions(predictions, output_file)


if __name__ == "__main__":
    args = parse_arguments()
    # main(args.input_file, args.model_file, args.output_file)

    # Test
    main("test_data.csv", "model_test.pkl", "predictions_test.json")

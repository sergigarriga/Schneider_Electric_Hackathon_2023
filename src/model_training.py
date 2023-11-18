import argparse
import os

import joblib
import pandas as pd

from config import (
    DATASET_PATH,
    MODEL_PATH,
)
from logger import get_logger
from models.models_config import models

logger = get_logger()


def load_data(file_path="processed_data.csv"):
    # Load data to train the model
    df = pd.read_csv(os.path.join(DATASET_PATH, file_path))
    return df


def split_data(df):
    # The test set is already provided in data/test_data.csv
    # Train data are the first 80% entries.
    # Validation data are the last 20% entries.
    X_train, X_val = df.iloc[: int(len(df) * 0.8), :-1], df.iloc[int(len(df) * 0.8) :, :-1]
    y_train, y_val = df.iloc[: int(len(df) * 0.8), -1], df.iloc[int(len(df) * 0.8) :, -1]
    return X_train, X_val, y_train, y_val


def train_model(model_name, model_instance, model_type, X_train, y_train, X_val=None, y_val=None):
    # Training of the model
    logger.info("-" * 50)
    logger.info(f"Training {model_name} model")

    if model_type != "custom":
        model_instance.fit(X_train, y_train)
    else:
        model_instance.train(X_train, y_train, X_val, y_val)
    return model_instance


def save_model(model, model_type, model_filename):
    # Save the model to a file
    if model_type != "custom":
        joblib.dump(model, os.path.join(MODEL_PATH, model_filename))
    else:
        model.save(os.path.join(MODEL_PATH, model_filename))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Model training script for Energy Forecasting Hackathon")
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/processed_data.csv",
        help="Path to the processed data file to train the model",
    )
    parser.add_argument("--model_file", type=str, default="models/model.pkl", help="Path to save the trained model")
    return parser.parse_args()


def main(input_file, model_filename):
    # Load data
    df = load_data(input_file)

    # We have a validation data if DL Model else we use all set of training data
    X_train, X_val, y_train, y_val = split_data(df)
    X, y = pd.concat([X_train, X_val]), pd.concat([y_train, y_val])

    for model in models:
        logger.info("-" * 50)
        logger.info(f"Training {model['name']} model")

        # Train the model
        model = (
            train_model(model["name"], model["model"], model["type"], X, y)
            if model["type"] != "custom"
            else train_model(model["name"], model["model"], model["type"], X_train, y_train, X_val, y_val)
        )

        # Save the model
        save_model(model, model["type"], model_filename)


if __name__ == "__main__":
    args = parse_arguments()
    # main(args.input_file, args.model_file)

    # Test
    main("processed_data.csv", "model_test.pkl")

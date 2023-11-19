import argparse
import os

import joblib
import pandas as pd

from config import (
    DATASET_PATH,
    MODELS_PATH,
)
from logger import get_logger
from models.models_config import models

from lazypredict.Supervised import LazyClassifier, LazyRegressor

logger = get_logger()


def load_data(file_path="processed_data.csv"):
    logger.info("Loading data...")

    # Load data to train the model
    df = pd.read_csv(os.path.join(DATASET_PATH, file_path))
    return df


def split_data(df):
    logger.info("Splitting data...")

    # The test set is already provided in data/test_data.csv
    # Train data are the first 80% entries.
    # Validation data are the last 20% entries.
    X_train, X_val = df.iloc[1 : int(len(df) * 0.8), 1:-1], df.iloc[int(len(df) * 0.8) :, 1:-1]
    y_train, y_val = df.iloc[1 : int(len(df) * 0.8), -1], df.iloc[int(len(df) * 0.8) :, -1]
    return X_train, X_val, y_train, y_val


def train_model(model_name, model_instance, model_type, X_train, y_train, X_val=None, y_val=None):
    logger.info(f"Training {model_name} model...")

    # Training of the model
    if model_type != "custom":
        model_instance.fit(X_train, y_train)
        # Log accuracy
        logger.info(f"Accuracy on training set: {model_instance.score(X_train, y_train)}")
    else:
        model_instance.train(X_train, y_train, X_val, y_val)
    return model_instance


def save_model(model, model_type, model_filename):
    logger.info("Saving model...")

    # Save the model to a file
    if model_type != "custom":
        joblib.dump(model, os.path.join(MODELS_PATH, model_filename))
    else:
        model.save(os.path.join(MODELS_PATH, model_filename))


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


def main(input_file, model_filename, models_set="lazy_predict"):
    # Load data
    df = load_data(input_file)

    # We have a validation data if DL Model else we use all set of training data
    X_train, X_val, y_train, y_val = split_data(df)
    X, y = pd.concat([X_train, X_val]), pd.concat([y_train, y_val])

    if models_set == "lazy_predict":
        clf = LazyClassifier(
            verbose=0,
            ignore_warnings=True,
            custom_metric=None,
            random_state=42,
        )
        lazy_models, predictions = clf.fit(X_train, X_val, y_train, y_val)

        print("Models:")
        print(lazy_models)
    else:
        for model in models.values():
            model_trained = (
                train_model(model["name"], model["instance"], model["type"], X, y)
                if model["type"] != "custom"
                else train_model(model["name"], model["instance"], model["type"], X_train, y_train, X_val, y_val)
            )

            # Save the model
            save_model(model_trained, model["type"], model_filename)


if __name__ == "__main__":
    logger.info("-" * 50)
    logger.info("Starting model training...")
    args = parse_arguments()
    # main(args.input_file, args.model_file)

    # Test
    main("processed_data.csv", "model_test.pkl")

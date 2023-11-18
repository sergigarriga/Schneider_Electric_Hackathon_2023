import torch

# -----------------------------------------
# Main parameters
# -----------------------------------------

EXECUTION_NAME = "test"
MODEL_NAME = "UNet"
OPTIMIZER = "Adam"
CRITERION = "MSELoss"

# -----------------------------------------

# Paths -----------------------------------
DATASET_PATH = "../data"
MODELS_PATH = "../models"
OUTPUTS_PATH = "../outputs"
LOGS_PATH = "../logs"

# Parameters ------------------------------
BATCH_SIZE_TRAIN = 256
BATCH_SIZE_TEST = 256
NUM_WORKERS = 12
EPOCHS = 10
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-5
MOMENTUM = 0.9
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

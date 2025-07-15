import importlib
import os
from unittest.mock import patch

import pytest

TEST_ENV_VARS = {
    "SERVER_IP": "1.1.1.1",
    "PORT": "5000",
    "CAMERA_INDEX": "0",
    "X_SERVO_PIN": "1",
    "Y_SERVO_PIN": "2",
    "CHARGE_PIN": "3",
    "LOAD_PIN": "4",
    "CAMERA_WIDTH": "640",
    "CAMERA_HEIGHT": "480",
    "CAMERA_BANDWIDTH_WIDTH_ANGLE": "90",
    "CAMERA_BANDWIDTH_HEIGHT_ANGLE": "70"
}

MODULES_TO_RELOAD = [
    "src.detection.color_detection",
    "src.detection.object_detection",
    "src.turret.camera",
    "src.turret.client",
    "src.turret.pi_controller",
]


@pytest.fixture(scope="session", autouse=True)
def setup_env_and_patch_load_dotenv():
    patchers = []
    for mod_name in MODULES_TO_RELOAD:
        patcher = patch(f"{mod_name}.load_dotenv")
        patcher.start()
        patchers.append(patcher)

    os.environ.update(TEST_ENV_VARS)

    for mod_name in MODULES_TO_RELOAD:
        mod = importlib.import_module(mod_name)
        importlib.reload(mod)

    yield

    for patcher in patchers:
        patcher.stop()

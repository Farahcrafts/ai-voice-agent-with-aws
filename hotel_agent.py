import os
import asyncio
import base64
import json
import boto3
import uuid
import warnings
import pyaudio
import pytz
import random
import hashlib
import datetime
import time
import inspect
from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.models import (
    InvokeModelWithBidirectionalStreamInputChunk,
    BidirectionalInputPayloadPart,
)
from aws_sdk_bedrock_runtime.config import Config
from smithy_aws_core.identity.environment import EnvironmentCredentialsResolver
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Suppress warnings
warnings.filterwarnings("ignore")

# Audio configuration
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024  # Number of frames per buffer

# Debug mode flag
DEBUG = False

def debug_print(message):
    """Print only if debug mode is enabled"""
    if DEBUG:
        functionName = inspect.stack()[1].function
        if functionName == "time_it" or functionName == "time_it_async":
            functionName = inspect.stack()[2].function
        print(
            "{:%Y-%m-%d %H:%M:%S.%f}".format(datetime.datetime.now())[:-3]
            + " "
            + functionName
            + " "
            + message
        )

#wrapper qui retourne le temps d'execution pour une tache synchrone 
def time_it(label, methodToRun):
    start_time = time.perf_counter()
    result = methodToRun()
    end_time = time.perf_counter()
    debug_print(f"Execution time for {label}: {end_time - start_time:.4f} seconds")
    return result

#wrapper qui retourne le temps d'execution pour une tache asynchrone 
async def time_it_async(label, methodToRun):
    start_time = time.perf_counter()
    result = await methodToRun()
    end_time = time.perf_counter()
    debug_print(f"Execution time for {label}: {end_time - start_time:.4f} seconds")
    return result


class ToolProcessor:
    def __init__(self):
        # ThreadPoolExecutor could be used for complex implementations
        self.tasks = {}
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.guest_table = self.dynamodb.Table("Hotel_Guests")
        self.reservation_table = self.dynamodb.Table("Hotel_Reservations")

        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

    
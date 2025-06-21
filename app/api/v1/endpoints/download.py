from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, FileResponse
from typing import Literal
import json
import os
import io
from datetime import datetime, timedelta

from app.services.storage_services import storage

from app.config import settings

router = APIRouter()


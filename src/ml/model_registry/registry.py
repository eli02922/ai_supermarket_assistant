import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """Model registry for managing ML models"""

    def __init__(self):
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        self.client = MlflowClient()

    def register_model(
        self,
        model_path: str,
        model_name: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Register a model in the registry"""
        try:
            # Create model version
            if version is None:
                version = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Register model
            model_uri = f"file://{model_path}"
            model_version = mlflow.register_model(
                model_uri,
                model_name,
                tags={
                    "version": version,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {}),
                }
            )

            logger.info(f"Registered model {model_name} version {version}")
            return model_version.version

        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            raise

    def get_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        stage: Optional[str] = None,
    ) -> Any:
        """Get a model from the registry"""
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            elif stage:
                model_uri = f"models:/{model_name}/{stage}"
            else:
                # Get latest version
                latest_version = self.get_latest_version(model_name)
                model_uri = f"models:/{model_name}/{latest_version}"

            model = mlflow.sklearn.load_model(model_uri)
            logger.info(f"Loaded model from {model_uri}")
            return model

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def get_latest_version(self, model_name: str) -> str:
        """Get the latest version of a model"""
        try:
            model_versions = self.client.get_latest_versions(model_name)
            if not model_versions:
                raise ValueError(f"No versions found for model {model_name}")

            # Sort by version number
            versions = sorted(
                [int(v.version) for v in model_versions],
                reverse=True,
            )
            return str(versions[0])

        except Exception as e:
            logger.error(f"Failed to get latest version: {str(e)}")
            raise

    def transition_model_stage(
        self,
        model_name: str,
        version: str,
        stage: str,
    ) -> None:
        """Transition model to a new stage"""
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
            )
            logger.info(f"Transitioned model {model_name} version {version} to {stage}")
        except Exception as e:
            logger.error(f"Failed to transition model stage: {str(e)}")
            raise
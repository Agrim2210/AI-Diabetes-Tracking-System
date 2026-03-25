from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.core.dependencies import get_db, get_current_user
from api.db import models
from api.schemas.prediction import PatientData, PredictionOut
from api.services.prediction_service import run_prediction

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictionOut, status_code=status.HTTP_201_CREATED)
def predict(
    patient_data: PatientData,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Run a diabetes prediction for the authenticated user.

    - Loads the trained model and scaler.
    - Preprocesses the 8 input features.
    - Assigns a risk level (Low / Medium / High) from the probability.
    - Persists the prediction to the database.
    - Returns the result with advice text.
    """
    prediction = run_prediction(
        patient_data=patient_data,
        user_id=current_user.id,
        db=db,
    )
    return prediction
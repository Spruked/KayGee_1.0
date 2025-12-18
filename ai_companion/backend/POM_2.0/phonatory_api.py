from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from POM.phonitory_output_module import PhonatoryOutputModule
import uvicorn
import os

app = FastAPI(title="Phonatory Output Module API")

class SpeechRequest(BaseModel):
    text: str
    pitch_factor: Optional[float] = 1.0
    formant_target: Optional[str] = None
    articulation: Optional[str] = None
    nasalization: Optional[str] = None
    output_filename: Optional[str] = None

# Initialize the phonatory module
phonatory = None

@app.on_event("startup")
async def startup_event():
    global phonatory
    try:
        phonatory = PhonatoryOutputModule()
        print("Phonatory Output Module initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Phonatory Output Module: {e}")
        raise

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Phonatory Output Module"}

@app.post("/speak")
async def generate_speech(request: SpeechRequest):
    """Generate speech from text input"""
    if phonatory is None:
        raise HTTPException(status_code=500, detail="Phonatory module not initialized")

    try:
        # Generate speech
        output_path = phonatory.phonate(
            text=request.text,
            pitch_factor=request.pitch_factor,
            formant_target=request.formant_target,
            articulation=request.articulation,
            nasalization=request.nasalization
        )

        # Return the audio file path or base64 encoded audio
        return {
            "status": "success",
            "text": request.text,
            "output_path": output_path,
            "message": f"Speech synthesized and saved to {output_path}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@app.post("/receive_cognitive_output")
async def receive_cognitive_output(cognitive_data: Dict[str, Any]):
    """Receive final cognitive output and convert to speech"""
    try:
        # Extract the harmonized response from cognitive processing
        harmonized_response = cognitive_data.get("harmonized_response", "")
        if not harmonized_response:
            harmonized_response = "Cognitive processing completed, but no response to vocalize."

        # Generate speech from the cognitive output
        speech_request = SpeechRequest(text=harmonized_response)
        result = await generate_speech(speech_request)

        return {
            "status": "cognitive_output_vocalized",
            "original_cognitive_data": cognitive_data,
            "speech_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive output vocalization failed: {str(e)}")

@app.get("/diagnostics")
async def run_diagnostics():
    """Run diagnostic checks on the phonatory system"""
    if phonatory is None:
        return {"status": "error", "message": "Phonatory module not initialized"}

    try:
        phonatory.diagnostics()
        return {"status": "diagnostics_logged", "message": "Diagnostics logged to synthesis.log"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
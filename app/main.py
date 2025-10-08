from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from .models import Offer, Lead
from .scoring import offer_storage, leads_storage, results_storage, score_leads
import os

app = FastAPI(title="Lead Scoring Service")

@app.post("/offer")
async def upload_offer(offer: Offer):
    """
    Upload product/offer details in JSON format.
    Example: {"name": "AI Outreach Automation", "value_props": ["24/7 outreach", "6x more meetings"], "ideal_use_cases": ["B2B SaaS mid-market"]}
    """
    global offer_storage
    offer_storage = offer
    return {"message": "Offer uploaded successfully"}

@app.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """
    Upload a CSV file containing leads with columns: name, role, company, industry, location, linkedin_bio.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        required_columns = ["name", "role", "company", "industry", "location", "linkedin_bio"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="CSV must contain columns: name, role, company, industry, location, linkedin_bio")
        
        global leads_storage
        leads_storage = [Lead(**row) for _, row in df.iterrows()]
        return {"message": f"Successfully uploaded {len(leads_storage)} leads"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.post("/score")
async def run_scoring():
    """
    Run the scoring pipeline on uploaded leads.
    """
    try:
        if not offer_storage or not leads_storage:
            raise HTTPException(status_code=400, detail="Offer or leads not uploaded")
        await score_leads()
        return {"message": f"Scored {len(results_storage)} leads successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@app.get("/results")
async def get_results():
    """
    Retrieve the scored leads as a JSON array.
    Example output: [{"name": "Ava Patel", "role": "Head of Growth", "company": "FlowMetrics", "intent": "High", "score": 85, "reasoning": "..."}]
    """
    if not results_storage:
        raise HTTPException(status_code=404, detail="No results available")
    return results_storage

@app.get("/export")
async def export_results():
    """
    Export the scored results as a CSV file (optional bonus feature).
    """
    if not results_storage:
        raise HTTPException(status_code=404, detail="No results available")
    
    try:
        df = pd.DataFrame([lead.dict() for lead in results_storage])
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue().encode()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=results.csv"}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
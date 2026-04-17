import httpx
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "static"))

PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def extract_cas(rn_list):
    cas_regex = re.compile(r'^\d{2,7}-\d{2}-\d$')
    for rn in rn_list:
        if cas_regex.match(rn):
            return rn
    return "N/A"

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/search")
async def search_compound(q: str = Query(..., description="Nome do medicamento ou composto")):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            cid_url = f"{PUBCHEM_BASE_URL}/compound/name/{q}/cids/JSON"
            cid_response = await client.get(cid_url)
            
            if cid_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
            
            cid = cid_response.json()["IdentifierList"]["CID"][0]

            props_url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,Title/JSON"
            props_res = await client.get(props_url)
            
            cas_url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/xrefs/RN/JSON"
            cas_res = await client.get(cas_url)
            
            if props_res.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro ao buscar propriedades.")
            
            prop_data = props_res.json()["PropertyTable"]["Properties"][0]
            
            cas_number = "N/A"
            if cas_res.status_code == 200:
                rn_data = cas_res.json().get("InformationList", {}).get("Information", [{}])[0].get("RN", [])
                cas_number = extract_cas(rn_data)

            return {
                "common_name": prop_data.get("Title", "N/A"),
                "iupac": prop_data.get("IUPACName", "N/A"),
                "cas": cas_number,
                "weight": prop_data.get("MolecularWeight", "N/A"),
                "formula": prop_data.get("MolecularFormula", "N/A"),
                "structure_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG",
                "cid": cid
            }
    except Exception as exc:
        if isinstance(exc, HTTPException): raise exc
        raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

import httpx
import re
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os

app = FastAPI()

# Configura diretório para arquivos estáticos
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)

templates = Jinja2Templates(directory=static_path)
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def extract_cas(rn_list):
    if not rn_list: return "N/A"
    cas_regex = re.compile(r'^\d{2,7}-\d{2}-\d$')
    for rn in rn_list:
        if isinstance(rn, str) and cas_regex.match(rn):
            return rn
    return "N/A"

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/search/advanced")
async def search_advanced(q: str = Query(..., description="Query booleana")):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            entrez_query = q.replace("[NAME]", "[Compound Name]") \
                            .replace("[MW]", "[Molecular Weight]") \
                            .replace("[CAS]", "[RN]") \
                            .replace("[HBOND_D]", "[Hydrogen Bond Donor Count]") \
                            .replace("[HBOND_A]", "[Hydrogen Bond Acceptor Count]") \
                            .replace("[FORMULA]", "[Formula]") \
                            .replace("[XLOGP]", "[XLogP]")

            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            esearch_res = await client.get(esearch_url, params={
                "db": "pccompound", "term": entrez_query, "retmode": "json", "retmax": 10
            })
            
            if esearch_res.status_code != 200:
                return {"results": [], "error": "Erro no serviço Entrez"}

            id_list = esearch_res.json().get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return {"results": []}

            cids_str = ",".join(id_list)
            props_task = client.get(f"{PUBCHEM_BASE_URL}/compound/cid/{cids_str}/property/MolecularFormula,MolecularWeight,IUPACName,Title/JSON")
            cas_task = client.get(f"{PUBCHEM_BASE_URL}/compound/cid/{cids_str}/xrefs/RN/JSON")
            
            props_res, cas_res = await asyncio.gather(props_task, cas_task)

            prop_map = {}
            if props_res.status_code == 200:
                for p in props_res.json().get("PropertyTable", {}).get("Properties", []):
                    prop_map[p["CID"]] = p

            cas_map = {}
            if cas_res.status_code == 200:
                for info in cas_res.json().get("InformationList", {}).get("Information", []):
                    cas_map[info["CID"]] = extract_cas(info.get("RN", []))

            final_results = []
            for cid_str in id_list:
                cid = int(cid_str)
                p = prop_map.get(cid, {})
                final_results.append({
                    "common_name": p.get("Title", "N/A"),
                    "iupac": p.get("IUPACName", "N/A"),
                    "cas": cas_map.get(cid, "N/A"),
                    "weight": p.get("MolecularWeight", "N/A"),
                    "formula": p.get("MolecularFormula", "N/A"),
                    "structure_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG",
                    "cid": cid
                })
            
            return {"results": final_results}

    except Exception as e:
        return {"results": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

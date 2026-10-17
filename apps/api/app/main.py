from datetime import datetime,timedelta,timezone
from enum import Enum
from typing import Optional
import os
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field

app=FastAPI(title="Haryana CMO Grievance API",version="0.1.0")
cors_origins=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

class Status(str,Enum):
 assigned="ASSIGNED"; in_progress="IN_PROGRESS"; awaiting="AWAITING_CITIZEN"; resolved="RESOLVED"; closed="CLOSED"

class GrievanceCreate(BaseModel):
 name:str=Field(min_length=2,max_length=100)
 mobile:str=Field(pattern=r"^[6-9]\d{9}$")
 language:str="hi"
 department:str
 category:str
 sub_category:str
 subject:str=Field(min_length=3,max_length=150)
 description:str=Field(min_length=20,max_length=4000)
 district:str
 location:str
 priority:str="NORMAL"

class Action(BaseModel):
 action:str
 note:str=Field(min_length=3,max_length=2000)

now=datetime.now(timezone.utc)
DB={
"CMHR-26-0000001-5":{"id":"CMHR-26-0000001-5","name":"Ravi Kumar","mobile":"9876543210","department":"Urban Local Bodies","category":"Civic services","sub_category":"Streetlight not working","subject":"Streetlight has not worked for two weeks","description":"The streetlight near the community centre has been off for two weeks, creating a safety issue at night.","district":"Gurugram","location":"Ward 14, Gurugram","office":"Municipal Corporation Gurugram","post":"Zone Officer","level":"L1","status":Status.in_progress,"received_at":now-timedelta(days=5),"due_at":now+timedelta(days=10),"flags":["verified"],"timeline":[{"at":now-timedelta(days=5),"text":"Grievance submitted","kind":"public"},{"at":now-timedelta(days=5),"text":"Auto-routed to Municipal Corporation Gurugram","kind":"system"}]},
"CMHR-26-0000002-2":{"id":"CMHR-26-0000002-2","name":"Sunita Devi","mobile":"9123456789","department":"SEWA","category":"Social security pension","sub_category":"Pension not credited this month","subject":"Old Age Samman Allowance not credited","description":"My pension has not been credited for this month.","district":"Hisar","location":"Hisar Tehsil","office":"District Social Welfare Office","post":"District Social Welfare Officer","level":"L2","status":Status.assigned,"received_at":now-timedelta(days=18),"due_at":now-timedelta(days=3),"flags":["senior_citizen","escalated"],"timeline":[{"at":now-timedelta(days=18),"text":"Grievance submitted","kind":"public"},{"at":now-timedelta(days=3),"text":"Escalated from L1 to L2 after SLA breach","kind":"system"}]}}

@app.get("/health")
def health(): return {"status":"ok","service":"haryana-cmo-api"}

@app.get("/api/v1/grievances")
def list_grievances(status:Optional[str]=None,district:Optional[str]=None):
 rows=list(DB.values())
 if status: rows=[x for x in rows if x["status"]==status]
 if district: rows=[x for x in rows if x["district"].lower()==district.lower()]
 return {"items":rows,"total":len(rows)}

@app.get("/api/v1/grievances/{gid}")
def get_grievance(gid:str):
 if gid not in DB: raise HTTPException(404,"Grievance not found")
 return DB[gid]

@app.post("/api/v1/grievances",status_code=201)
def create_grievance(payload:GrievanceCreate):
 seq=len(DB)+1
 gid=f"CMHR-26-{seq:07d}-0"
 current=datetime.now(timezone.utc)
 item=payload.model_dump()|{"id":gid,"office":"District Grievance Cell","post":"L1 Grievance Officer","level":"L1","status":Status.assigned,"received_at":current,"due_at":current+timedelta(days=15),"flags":[],"timeline":[{"at":current,"text":"Grievance submitted","kind":"public"},{"at":current,"text":"Queued for automatic routing","kind":"system"}]}
 DB[gid]=item
 return item

@app.post("/api/v1/grievances/{gid}/actions")
def action(gid:str,payload:Action):
 if gid not in DB: raise HTTPException(404,"Grievance not found")
 g=DB[gid]
 if payload.action not in {"resolve","return","request_info","extend","escalate"}: raise HTTPException(400,"Unsupported action")
 current=datetime.now(timezone.utc)
 if payload.action=="resolve": g["status"]=Status.resolved;text="Officer marked the case resolved"
 elif payload.action=="escalate":
  if g["level"]=="L3": raise HTTPException(400,"Already at L3")
  old=g["level"];g["level"]=f"L{int(old[1:])+1}";g["status"]=Status.assigned;g["due_at"]=current+timedelta(days=15);g["flags"]=list(set(g["flags"]+["escalated"]));text=f"Manually escalated from {old} to {g['level']}"
 elif payload.action=="request_info": g["status"]=Status.awaiting;text="Additional information requested from citizen"
 elif payload.action=="extend": g["due_at"]=current+timedelta(days=15);text="Extension requested"
 else: text="Returned to routing desk"
 g["timeline"].append({"at":current,"text":f"{text}: {payload.note}","kind":"internal"})
 return g

@app.post("/api/v1/jobs/escalate")
def run_escalation():
 changed=[];current=datetime.now(timezone.utc)
 for g in DB.values():
  if g["status"] in {Status.resolved,Status.closed} or g["due_at"]>current: continue
  level=int(g["level"][1:])
  if level<3:
   old=g["level"];g["level"]=f"L{level+1}";g["due_at"]=current+timedelta(days=15);g["flags"]=list(set(g["flags"]+["escalated"]));g["timeline"].append({"at":current,"text":f"Automatic SLA breach: {old} → {g['level']}","kind":"system"});changed.append(g["id"])
  elif "l3_breach" not in g["flags"]:
   g["flags"].append("l3_breach");g["timeline"].append({"at":current,"text":"L3 breach added to CMO red list","kind":"system"});changed.append(g["id"])
 return {"changed":changed}

@app.get("/api/v1/dashboard/summary")
def summary():
 rows=list(DB.values());current=datetime.now(timezone.utc)
 return {"total":len(rows),"open":sum(x["status"] not in {Status.closed,Status.resolved} for x in rows),"breached":sum(x["due_at"]<current and x["status"] not in {Status.closed,Status.resolved} for x in rows),"resolved":sum(x["status"]==Status.resolved for x in rows),"l3":sum(x["level"]=="L3" for x in rows),"satisfaction":76,"avg_resolution_days":12.4}

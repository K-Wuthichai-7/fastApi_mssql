from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import db_connection
from pydantic import BaseModel
from datetime import time, date ,datetime
from typing import Optional
import pyodbc  


app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Status(BaseModel):
    id: int
    batchId: str
    key_value: str  
    adjust: Optional[float] = None
    batch: str
    finish_time: Optional[str] = None  
    ft9355: Optional[float] = None
    ft9401: Optional[float] = None
    interface_tank: Optional[str] = None
    meterCumulative: Optional[str] = None
    planedVolume: Optional[float] = None
    reinjectVolume: Optional[float] = None
    remark: Optional[str] = None
    specify: Optional[str] = None
    status: Optional[str] = None
    supply_tank: str
    date: date
    meter: str
    c_supply_tank: Optional[str] = None
    n_batch: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
    
class BatchRequest(BaseModel):
    batch: str

# connect database
@app.get("/")
async def test_connection():
    try:
        conn = db_connection()
        conn.close()
        return {"message": "Connection successful"}
    except pyodbc.Error as e:
        return {"error": str(e)}

# convert to list
def dict_list(cursor, rows):
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]
    return result


@app.get("/read_status")
async def read_status():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM t_mtp_status ORDER BY date, finish_time, start_time")
        rows = cursor.fetchall()
        result = dict_list(cursor, rows)
        conn.close()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# read status by id
@app.get("/read_status/{id}")
async def read_status(id: int):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM t_mtp_status WHERE id = ?", (id,))
        rows = cursor.fetchall()
        result = dict_list(cursor, rows)
        conn.close()
        if not rows:
            raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# read status by batchId
@app.post("/read_batch")
async def read_status(batch: BatchRequest):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM t_mtp_status WHERE batch = ?  ORDER BY date, finish_time", (batch.batch,) )
        rows = cursor.fetchall()
        result = dict_list(cursor, rows)
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"Item with batch {batch.batch} not found")
        
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
# create a new status
@app.post("/status")
async def create_status(status: Status):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        columns = (
            "[batchId], [keys], [adjust], [batch], [finish_time], [ft9355], "
            "[ft9401], [interface_tank], [meterCumulative], [planedVolume], [reinjectVolume], "
            "[remark], [specify], [status], [supply_tank], [date],"
            "[meter], [c_supply_tank], [n_batch]"
        )
        placeholders = ", ".join(["?" for _ in range(19)])
        values = [
            status.batchId, status.key_value, status.adjust, status.batch,
            status.finish_time, status.ft9355, status.ft9401, status.interface_tank,
            status.meterCumulative, status.planedVolume, status.reinjectVolume, status.remark,
            status.specify, status.status, status.supply_tank, status.date,
            status.meter, status.c_supply_tank, status.n_batch
        ]

        query = f"INSERT INTO [runsheet].[dbo].[t_mtp_status] ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "ok"}


# update status by id
@app.put("/update_status")
async def update_status(status: Status):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        query = """
        UPDATE [runsheet].[dbo].[t_mtp_status]
        SET 
            [batchId] = ?, 
            [keys] = ?, 
            [adjust] = ?, 
            [batch] = ?, 
            [finish_time] = ?, 
            [ft9355] = ?, 
            [ft9401] = ?, 
            [interface_tank] = ?, 
            [meterCumulative] = ?, 
            [planedVolume] = ?, 
            [reinjectVolume] = ?, 
            [remark] = ?, 
            [specify] = ?, 
            [status] = ?, 
            [supply_tank] = ?, 
            [date] = ?,
            [meter] = ?,
            [c_supply_tank] =?,
            [n_batch] =?

        WHERE [id] = ?
        """
        values = [
            status.batchId, status.key_value, status.adjust, status.batch,
            status.finish_time, status.ft9355, status.ft9401, status.interface_tank,
            status.meterCumulative, status.planedVolume, status.reinjectVolume, status.remark,
            status.specify, status.status, status.supply_tank, status.date,
            status.meter, status.c_supply_tank, status.n_batch, status.id
        ]

        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "ok"}


#delete status by id
@app.delete("/delete_status/{id}")
async def delete_status(id: int):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM [runsheet].[dbo].[t_mtp_status] WHERE [id] = ?"
        cursor.execute(query, (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "ok"}

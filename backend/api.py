from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

DB_PATH = os.path.join(os.path.dirname(__file__), "params.db")
DB = DB_PATH

class GroupCreate(BaseModel):
    name: str

class ElementCreate(BaseModel):
    name: str
    group_id: int

def sql(query, args=(), fetch_one=False, fetch_all=False):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        if fetch_one:
            row = cur.fetchone()
            return dict(row) if row else None
        if fetch_all:
            return [dict(row) for row in cur.fetchall()]
        conn.commit()
        return cur.lastrowid

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        conn.execute("CREATE TABLE IF NOT EXISTS elements (id INTEGER PRIMARY KEY, name TEXT, group_id INTEGER REFERENCES groups)")
        conn.execute("CREATE TABLE IF NOT EXISTS group_params (group_id INTEGER, param_name TEXT, param_value TEXT, PRIMARY KEY(group_id, param_name))")
        conn.execute("CREATE TABLE IF NOT EXISTS element_params (element_id INTEGER, param_name TEXT, param_value TEXT, PRIMARY KEY(element_id, param_name))")

init_db()

@app.get("/groups")
def get_groups():
    return sql("SELECT * FROM groups", fetch_all=True)

@app.post("/groups")
def create_group(group: GroupCreate):
    group_id = sql("INSERT INTO groups (name) VALUES (?)", (group.name,))
    return {"id": group_id, "name": group.name}

@app.delete("/groups/{id}")
def delete_group(id: int):
    sql("DELETE FROM element_params WHERE element_id IN (SELECT id FROM elements WHERE group_id=?)", (id,))
    sql("DELETE FROM elements WHERE group_id=?", (id,))
    sql("DELETE FROM group_params WHERE group_id=?", (id,))
    sql("DELETE FROM groups WHERE id=?", (id,))
    return {"ok": True}

@app.get("/elements")
def get_elements():
    return sql("SELECT * FROM elements", fetch_all=True)

@app.post("/elements")
def create_element(element: ElementCreate):
    element_id = sql("INSERT INTO elements (name, group_id) VALUES (?,?)", (element.name, element.group_id))
    return {"id": element_id, "name": element.name, "group_id": element.group_id}

@app.delete("/elements/{id}")
def delete_element(id: int):
    sql("DELETE FROM element_params WHERE element_id=?", (id,))
    sql("DELETE FROM elements WHERE id=?", (id,))
    return {"ok": True}

@app.get("/groups/{id}/params")
def get_group_params(id: int):
    rows = sql("SELECT param_name, param_value FROM group_params WHERE group_id=?", (id,), fetch_all=True)
    result = {}
    for row in rows:
        result[row["param_name"]] = row["param_value"]
    return result

@app.put("/groups/{id}/params")
def set_group_params(id: int, params: dict):
    sql("DELETE FROM group_params WHERE group_id=?", (id,))
    for name, value in params.items():
        sql("INSERT INTO group_params (group_id, param_name, param_value) VALUES (?,?,?)", (id, name, value))
    return {"ok": True}

@app.get("/elements/{id}/resolved_params")
def get_resolved_params(id: int):
    el = sql("SELECT group_id FROM elements WHERE id=?", (id,), fetch_one=True)
    if not el:
        raise HTTPException(404, "Element not found")
    
    group_rows = sql("SELECT param_name, param_value FROM group_params WHERE group_id=?", (el["group_id"],), fetch_all=True)
    group = {}
    for row in group_rows:
        group[row["param_name"]] = row["param_value"]
    
    over_rows = sql("SELECT param_name, param_value FROM element_params WHERE element_id=?", (id,), fetch_all=True)
    over = {}
    for row in over_rows:
        over[row["param_name"]] = row["param_value"]
    
    resolved = group.copy()
    resolved.update(over)
    inherited = {k: v for k, v in group.items() if k not in over}
    
    return {"resolved": resolved, "inherited": inherited, "overridden": over}

@app.put("/elements/{id}/params")
def set_element_params(id: int, params: dict):
    sql("DELETE FROM element_params WHERE element_id=?", (id,))
    for name, value in params.items():
        sql("INSERT INTO element_params (element_id, param_name, param_value) VALUES (?,?,?)", (id, name, value))
    return {"ok": True}

app.mount("/css", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/js")), name="js")
app.mount("/images", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/images")), name="images")
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/html")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

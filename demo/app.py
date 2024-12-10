
import datetime
from typing import Annotated, Optional
from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class Order(BaseModel):
    number : int
    startDate : datetime.date
    orgt : str
    model : str
    description_problem : Optional [str] = ""
    problem_type : str
    fio : str
    phone : str
    status : Optional[str] = ""
    master : Optional[str] = "Не назначен"
    materials : Optional[str] = ""
    parts : Optional[str] = ""
    endDate : Optional[datetime.date] = None
    comments : Optional[list] = []

repo = [
    Order(
        number = 1,
        startDate = "2002-05-15",
        orgt = "Принтер",
        model = "Sony XBOX",
        problem_type = "Не печатает",
        description_problem = "Схавал бумагу и умер",
        fio = "Валера Валерий Валерьевич",
        phone = "88005553535",
        status = "новая заявка"
    ),
    Order(
        number = 2,
        startDate = "2006-02-20",
        orgt = "Сканер",
        model = "VR",
        problem_type = "Не сканирует",
        description_problem = "Сели сканировать жопу и сломали",
        fio = "Санья Подзабоный Залупочёсов",
        phone = "88005553505",
        status = "в работе"
    )
]

message = ""

class OrderUpdateDTO(BaseModel):
    number : int
    status : Optional[str] = ""
    description_problem : Optional [str] = ""
    master : Optional[str] = ""
    materials : Optional[str] = ""
    parts : Optional[str] = ""
    comment : Optional[str] = str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/orders")
def get_orders(param = None):
    global message
    buffer = message
    message = ""
    if(param):
        return{"repo" : [o for o in repo if o.number == int(param)], "message" : buffer}
    return {"repo" : repo, "message" : buffer}

@app.post("/create")
def create_orders(dto : Annotated[Order, Form()]):
    repo.append(dto)

@app.post("/update")
def update_orders(dto : Annotated[OrderUpdateDTO, Form()]):
    global message
    for o in repo:
        if o.number == dto.number:
            if dto.status != o and dto.status != "":
                o.status = dto.status
                message = f"Статус заявки №{o.number} был изменён"
                if o.status == "завершена":
                    message = f"Заявка №{o.number} завершена"
                    o.endDate = datetime.datetime.now()
            if dto.description_problem != "":
                o.problem_type = dto.description_problem
            if dto.master != "":
                o.master = dto.master
            if dto.materials != o and dto.materials != "":
                o.materials = dto.materials
            if dto.parts != o and dto.parts != "":
                o.parts = dto.parts
            if dto.comment != None and dto.comment != "":
                o.comments.append(dto.comment)
            return o
    return "Не найдено"

def complete_count():
    a = [o for o in repo if o.status == "завершена"]
    return len(a)

def get_problem_type_stat():
    dict = {}
    for o in repo:
        if o.problem_type in dict.keys():
            dict[o.problem_type] += 1
        else:
            dict[o.problem_type] = 1
    return dict

def avg_time_to_complete():
    times = [(
            datetime.datetime(o.endDate.year, o.endDate.month, o.endDate.day) -
            datetime.datetime(o.startDate.year, o.startDate.month, o.startDate.day)).days
                    for o in repo
                    if o.status == "завершена"]
    if complete_count() != 0:
        return sum(times) / complete_count()
    return 0

@app.get("/stat")
def get_stats():
    return {
        "complete_count" : complete_count(),
        "problem_type_stat" : get_problem_type_stat(),
        "avg_time_to_complete" : avg_time_to_complete()
    }
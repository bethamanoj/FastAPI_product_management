from fastapi import FastAPI,Request,Form,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_connection

app = FastAPI()

templates = Jinja2Templates(directory = "templates")

app.mount(
    "/static",
    StaticFiles(directory = "static"),
    name = "static"
)

@app.get('/')
def home():
    return RedirectResponse(url='/products',status_code=303)

@app.get('/products')
def view_products(request : Request,search: str =""):
    connection = get_connection()
    cursor = connection.cursor(dictionary = True)
    try:
        if search.strip():
            sql = "SELECT * FROM products WHERE name LIKE %s ORDER BY id desc"
            cursor.execute(sql,(f"%{search.strip()}%",))
        else:
            cursor.execute('SELECT * FROM products ORDER BY id DESC')
        products = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return templates.TemplateResponse(
        request = request,
        name = "products.html",
        context = {
            'products':products,
            "search" : search
            }
    )

@app.get('/products/add')
def add_product(request:Request):
    return templates.TemplateResponse(
        request = request,
        name = 'add_products.html',
        context={}
    )

@app.post('/products/add')
def create_product(
    request: Request,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    image: str = Form(...)
):
    if price<0 or quantity<0:
        raise HTTPException(
            status_code=400,
            detail="Price or Stock cannot be negative"
        )
    connection = get_connection()
    cursor = connection.cursor()
    try:
        sql = """
insert into products(name,price,description,quantity,image)
values (%s,%s,%s,%s,%s)
"""
        cursor.execute(sql,(name,price,description,quantity,image))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    return RedirectResponse(url="/products",status_code=303)

@app.post('/products/delete/{product_id}')
def delete_product(product_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('DELETE FROM products where id = %s',(product_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    return RedirectResponse(url='/products',status_code=303)

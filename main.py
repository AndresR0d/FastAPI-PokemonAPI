from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastui import FastUI, prebuilt_html, components as c
from fastui.events import GoToEvent
from pydantic import BaseModel
import httpx

# Rebuild Navbar component to handle AnyComponent
c.Navbar.model_rebuild()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Pokemon(BaseModel):
    name: str
    sprite: str
    types: list[str]

async def fetch_pokemon(name: str) -> Pokemon:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'https://pokeapi.co/api/v2/pokemon/{name.lower()}')
            resp.raise_for_status()
            data = resp.json()
            return Pokemon(
                name=data['name'],
                sprite=data['sprites']['front_default'],
                types=[t['type']['name'] for t in data['types']],
            )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail="Pokémon not found")

@app.get("/api/pokemon/{name}", response_model=FastUI, response_model_exclude_none=True)
async def get_pokemon(name: str):
    try:
        pokemon = await fetch_pokemon(name)
        return [
            c.PageTitle(text=f'{pokemon.name.capitalize()} — Pokémon'),
            c.Navbar(title='Pokémon Finder', title_event=GoToEvent(url='/')),
            c.Div(
                components=[
                    c.Heading(text=pokemon.name.capitalize(), level=2),
                    c.Image(src=pokemon.sprite, alt=pokemon.name, width=200, height=200),
                    c.Div(
                        components=[
                            c.Span(text=type_name, class_name='badge bg-blue-500 text-white mx-1')
                            for type_name in pokemon.types
                        ],
                        class_name='my-2',
                    ),
                ],
                class_name='container mx-auto p-4',
            ),
        ]
    except HTTPException as e:
        return [
            c.PageTitle(text='Error — Pokémon Finder'),
            c.Navbar(title='Pokémon Finder'),
            c.Div(
                components=[
                    c.Heading(text='Error', level=2),
                    c.Paragraph(text=e.detail),
                ],
                class_name='container mx-auto p-4 text-red-500',
            ),
        ]

@app.get('/{path:path}')
async def html_landing():
    return prebuilt_html(title='Pokémon Finder')
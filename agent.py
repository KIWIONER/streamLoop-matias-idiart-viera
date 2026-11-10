import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"
API_BASE_URL = "http://127.0.0.1:8000"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Obtiene la lista completa de todos los productos en el inventario con sus cantidades actuales.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_product",
            "description": "Añade un nuevo producto al inventario. Usar solo cuando un producto es totalmente nuevo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del producto"},
                    "quantity": {"type": "integer", "description": "Cantidad inicial"},
                    "unit": {"type": "string", "description": "Unidad (ej. kg, litros, cajas)"}
                },
                "required": ["name", "quantity", "unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_product",
            "description": "Actualiza el stock de un producto existente. Puedes sumar o restar stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "El ID del producto a actualizar"},
                    "delta": {"type": "integer", "description": "La cantidad a modificar. Positivo si entra stock, negativo si sale o se vende."}
                },
                "required": ["product_id", "delta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_alerts",
            "description": "Obtiene una lista de los productos que tienen bajo stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold": {"type": "integer", "description": "Umbral de alerta. Por defecto es 10."}
                }
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Ejecuta la llamada HTTP a nuestra API de FastAPI según la herramienta seleccionada."""
    try:
        if tool_name == "get_inventory":
            response = requests.get(f"{API_BASE_URL}/inventory")
            
        elif tool_name == "add_product":
            response = requests.post(f"{API_BASE_URL}/inventory", json=tool_args)
            
        elif tool_name == "update_product":
            product_id = tool_args.pop("product_id")
            # Enviamos 'delta' en el body según nuestro ProductUpdate
            response = requests.patch(f"{API_BASE_URL}/inventory/{product_id}", json=tool_args)
            
        elif tool_name == "get_alerts":
            threshold = tool_args.get("threshold", 10)
            response = requests.get(f"{API_BASE_URL}/inventory/alerts", params={"threshold": threshold})
            
        else:
            return json.dumps({"error": f"Herramienta {tool_name} desconocida"})
        # Retornamos el JSON como un string para que el LLM lo pueda leer
        if response.status_code >= 400:
            return json.dumps({"error": response.json()})
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

import csv
import datetime

LOG_FILE = "conversation_log.csv"

def log_event(actor: str, message: str, tool_call: str = ""):
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["actor", "message", "tool_call", "timestamp"])

        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        writer.writerow([actor, message, tool_call, timestamp])


def run_agent():
    print("🤖 Asistente de Inventario IA iniciado. (Escribe 'salir' para terminar)")
    
    # Instrucciones base (System Prompt)
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente de inventario muy útil para una cafetería. "
                "Puedes usar herramientas para consultar y modificar el stock. "
                "Responde de forma concisa y amigable."
            )
        }
    ]
    while True:
        # OBSERVACIÓN: Leer input del usuario
        user_input = input("\nTú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("🤖 ¡Hasta luego!")
            break
            
        # Añadir al historial y registrar en el log
        messages.append({"role": "user", "content": user_input})
        log_event("user", user_input)
        # Bucle interno de llamadas a tools (PENSAR -> ACTUAR -> ACTUALIZAR)
        while True:
            # PENSAR: Llamar al LLM
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # Revisar si el LLM decidió usar una herramienta
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 [Ejecutando tool: {function_name}({function_args})]")
                    log_event("agent", f"Calling tool: {function_name}", function_name)
                    
                    # ACTUAR: Llamar a la API
                    tool_result = execute_tool(function_name, function_args)
                    
                    # ACTUALIZAR: Inyectar el resultado al contexto
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_result
                    })
                    
                    log_event("tool", tool_result, function_name)
                    
                # Volver al inicio del bucle interno para que el LLM lea el resultado de la tool
                continue 
                
            else:
                # Si no hay tool calls, es la respuesta final al usuario
                final_text = response_message.content
                print(f"🤖 Agente: {final_text}")
                log_event("agent", final_text)
                
                # Rompemos el bucle interno, y esperamos el siguiente input del usuario
                break
if __name__ == "__main__":
    # Arrancar el agente
    run_agent()

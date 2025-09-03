import pandas as pd
import re 

def format_duration_to_minutes(value) -> str:
    """
    Converte uma string de duração (ex: "1h 30m") para o total de minutos (ex: "90").
    """
    # Garante que o valor é uma string
    value_str = str(value)
    
    # Usa expressão regular para extrair os números de horas e minutos
    match = re.search(r'(\d+)\s*h\s*(\d+)\s*m', value_str, re.IGNORECASE)
    
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        total_minutes = (hours * 60) + minutes
        return str(total_minutes)
    
    # Se o formato não corresponder, retorna "0" como um padrão seguro
    return "0"

def format_date_value(value) -> dict:
    """
    Formata um valor para uma coluna de Data do Monday.
    Ele lida com valores que podem ser apenas data ou data e hora.
    """
    # Converte o valor para um objeto datetime do pandas para facilitar a manipulação
    try:
        dt_object = pd.to_datetime(value)
    except (ValueError, TypeError):
        # Se não for possível converter, retorna um dicionário vazio ou lança um erro
        # para indicar que o dado de origem está inválido.
        return {}

    # Extrai a parte da data no formato AAAA-MM-DD
    date_str = dt_object.strftime('%Y-%m-%d')
    
    # Verifica se o horário é significativo (diferente de meia-noite)
    if dt_object.hour == 0 and dt_object.minute == 0 and dt_object.second == 0:
        # Se for meia-noite, envia apenas a data
        return {"date": date_str}
    else:
        # Se houver horário, envia a data e a hora em chaves separadas
        time_str = dt_object.strftime('%H:%M:%S')
        return {"date": date_str, "time": time_str}


def format_status_value(value) -> dict:
    """
    Formata valores para colunas de Status/Cor, normalizando booleanos.
    """
    # Converte booleanos Python para as strings 'true'/'false' em minúsculas
    if isinstance(value, bool):
        value = str(value).lower()
    
    # Se o valor for a string "False" ou "True", converte para minúsculas
    str_value = str(value)
    if str_value.lower() in ["true", "false"]:
        return {"label": str_value.lower()}
    
    # Para todos os outros casos, usa o valor como está
    return {"label": str_value}

COLUMN_FORMATTERS = {
    "status": format_status_value,
    "color": format_status_value,
    "date": format_date_value,
    "people": lambda v: {"personsAndTeams": [{"id": int(v), "kind": "person"}]},
    "numeric": lambda v: str(v),  # A API espera números como strings
    "link": lambda v: {"url": str(v), "text": str(v)}, # Para links, usamos o valor como URL e texto
    "long_text": lambda v: {"text": str(v)},
    "text": lambda v: str(v)
}
# Formatador padrão para tipos não listados acima (trata como texto simples)
DEFAULT_FORMATTER = lambda v: str(v)

ID_SPECIFIC_FORMATTERS = {
    "numeric4": format_duration_to_minutes
    # Adicione aqui outras colunas que precisem de tratamento especial no futuro
}
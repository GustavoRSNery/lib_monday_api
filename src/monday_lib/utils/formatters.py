COLUMN_FORMATTERS = {
    "status": lambda v: {"label": str(v)},
    "date": lambda v: {"date": str(v)},
    "people": lambda v: {"personsAndTeams": [{"id": int(v), "kind": "person"}]},
    "numeric": lambda v: str(v),  # A API espera números como strings
    "link": lambda v: {"url": str(v), "text": str(v)}, # Para links, usamos o valor como URL e texto
    "long_text": lambda v: {"text": str(v)},
    "text": lambda v: str(v)
}
# Formatador padrão para tipos não listados acima (trata como texto simples)
DEFAULT_FORMATTER = lambda v: str(v)
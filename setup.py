from setuptools import setup, find_packages #type:ignore

def parse_requirements(filename):
    with open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

texto = "Versão 0.1.1 Extração e manipulação de dados Monday.com para o Sicoob" \
        "Versão 0.1.2 (É possível extrair items sem o filtro de Data)" \
        "Versão 0.1.3 (Otimização da chamada API & tratamento de erros de 'response')" \
        "Versão 0.2.0 (Refatoração completa para arquitetura modular, adiciona criação de itens em lote e funções para criar/deletar/buscar grupos, implementa logging de auditoria)"

setup(
    name="extracao_monday",
    version="0.2.0",
    description=texto,
    author="Gustavo Nery",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
    python_requires=">=3.11",
)

import black
import json
import textwrap
import re
import os

def get_spaces_map(workspace_client) -> dict:
    """
    Mapeia todos os espaços Genie existentes no workspace.

    Busca a lista de espaços na API apenas uma vez e cria um dicionário
    para buscas O(1) pelo título do espaço.

    Returns:
        dict: Dicionário no formato {'Título do Espaço': 'ID_do_Espaco'}.
    """
    return {
        space.title: space.space_id
        for space in workspace_client.genie.list_spaces().spaces
    }

INDENT = "    "  # 4 espaços

def fix_payload_content(content: str) -> str:
    """
    Arruma os ids do payload de um genie substituindo os ids antigos por novos ids gerados aleatoriamente
    com "uuid.uuid4().hex".
    
    Args:
        content (str): Conteúdo do payload.
    """

    # Importa bibliotecas necessárias
    if "import uuid" not in content:
        content = content.replace("import textwrap", "import textwrap\nimport uuid")

    # Substitui "id": "any_hex_string" por "id": uuid.uuid4().hex
    pattern = r"\"id\":\s*\"[a-f0-9]{32}\""
    replacement = '"id": uuid.uuid4().hex'

    new_content = re.sub(pattern, replacement, content)

    return new_content

def refactor_payload_content(content: str) -> str:
    """
    Refatora o payload do genie para substituir campos baseados em listas
    (content, sql) por strings multilinha usando textwrap.dedent.
    """
    lines = content.splitlines(True)

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detecta os campos que devem ser refatorados
        if ('"content": [' in line or '"sql": [' in line or "'content': [" in line or "'sql': [" in line) and "]" not in line:
            indent = line[: line.find('"')] if '"' in line else line[: line.find("'")]
            field_name = "content" if "content" in line else "sql"

            # Coleta as linhas até o colchete de fechamento
            block_lines = []
            i += 1
            while i < len(lines) and "]" not in lines[i]:
                block_lines.append(lines[i].strip())
                i += 1

            # Processa as strings coletadas
            extracted_text = []
            for bl in block_lines:
                # Remove o " inicial e o " final, ou \r\n",
                clean_line = bl
                if clean_line.startswith('"') or clean_line.startswith("'"):
                    clean_line = clean_line[1:]

                # Remove a vírgula final
                if clean_line.endswith(","):
                    clean_line = clean_line[:-1]

                # Remove o " ou ' final
                if clean_line.endswith('"') or clean_line.endswith("'"):
                    clean_line = clean_line[:-1]

                # Remove o \r\n (Padrão Windows)
                clean_line = clean_line.replace("\\r\\n", "\n")
                
                # Remove o \n (Padrão Unix)
                clean_line = clean_line.replace("\\n", "\n")
                
                # Remove o \"
                clean_line = clean_line.replace('\\"', '"')

                extracted_text.append(clean_line)

            full_text = "".join(extracted_text)

            # Cria o bloco textwrap.dedent encapsulado em uma lista
            new_lines.append(f'{indent}"{field_name}": [\n')
            new_lines.append(f'{indent}{INDENT}textwrap.dedent("""\\\n')
            for text_line in full_text.splitlines():
                new_lines.append(f"{indent}{INDENT * 4}{text_line}\n")
            new_lines.append(f'{indent}{INDENT * 4}""")\n')
            new_lines.append(f"{indent}],\n")

            i += 1  # Avança além do ]
        else:
            new_lines.append(line)
            i += 1

    return "".join(new_lines)

def create_metadata_content(workspace_client, genie_resource_id: str, metadata_getter_function_name: str) -> str:
    """
    Gera a string de código python com os metadados brutos de um recurso Genie.
    """
    genie_space = workspace_client.genie.get_space(genie_resource_id, include_serialized_space=True)
    
    title = genie_space.title
    description = genie_space.description
    
    serialized_space_attr = genie_space.serialized_space
    if hasattr(serialized_space_attr, "as_dict"):
        serialized_space = serialized_space_attr.as_dict()
    elif isinstance(serialized_space_attr, str):
        try:
            serialized_space = json.loads(serialized_space_attr)
        except json.JSONDecodeError:
            serialized_space = serialized_space_attr
    else:
        serialized_space = serialized_space_attr

    serialized_space_str = json.dumps(serialized_space, indent=4, ensure_ascii=False)
    serialized_space_str = serialized_space_str.replace(": null", ": None").replace(": true", ": True").replace(": false", ": False")
    
    # Identar corretamente
    lines = serialized_space_str.split('\n')
    indented_lines = [lines[0]] + ['        ' + line for line in lines[1:]]
    serialized_space_formatted = '\n'.join(indented_lines)

    # Formatar o description com textwrap.dedent
    desc_lines = description.split('\n')
    desc_formatted = '\n'.join([f"{INDENT * 6}{line}" for line in desc_lines])

    file_content = textwrap.dedent(f"""\
        import textwrap

        def {metadata_getter_function_name}():
            return {{
                "title": {repr(title)},
                "description": textwrap.dedent(\"\"\"\\
{desc_formatted}
                    \"\"\"),
                "serialized_space": {serialized_space_formatted}
            }}
        """)

    return file_content

def generate_metadata(
    workspace_client,
    genie_resource_id: str,
    metadata_getter_function_name: str,
    path: str
):
    """
    Orquestra a geração, limpeza e formatação dos metadados de um recurso Genie, e salva no disco.
    """
    # Cria o metadado
    content = create_metadata_content(
        workspace_client,
        genie_resource_id,
        metadata_getter_function_name
    )

    # Limpa / Arruma os IDs
    content = fix_payload_content(content)

    # Refatora para usar textwrap
    content = refactor_payload_content(content)

    # Formata com black em memória
    try:
        content = black.format_str(content, mode=black.Mode())
    except Exception as e:
        print(f"Aviso: não foi possível formatar com black: {e}")

    # Salva no disco
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
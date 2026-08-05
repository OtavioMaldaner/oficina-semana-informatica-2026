import json
import copy
from pathlib import Path

from pydantic import BaseModel
from databricks.sdk.service.dashboards import GenieSpace
from databricks.sdk import WorkspaceClient

from .utils import get_spaces_map

class GenieMetadata(BaseModel):
    title: str
    description: str
    raw_serialized_space: dict
    parent_path : str | None = None

    def _correct_data_sources(self, space_data: dict) -> None:
        """
        Extrai e formata as fontes de dados do espaço, ordenando as tabelas pelo identifier.

        Args:
            space_data (dict): O dicionário de metadados mutável do espaço.
        """
        if 'data_sources' in space_data:
            # data_sources é diretamente um dicionário
            if isinstance(space_data['data_sources'], dict):
                if 'tables' in space_data['data_sources']:
                    space_data['data_sources']['tables'] = sorted(
                        space_data['data_sources']['tables'], 
                        key=lambda t: str(t.get('identifier', ''))
                    )
            # data_sources é uma lista
            elif isinstance(space_data['data_sources'], list):
                for data_source in space_data['data_sources']:
                    if isinstance(data_source, dict) and 'tables' in data_source:
                        data_source['tables'] = sorted(
                            data_source['tables'], 
                            key=lambda t: str(t.get('identifier', ''))
                        )
    
    def _correct_instructions(self, space_data: dict) -> None:
        """
        Extrai e formata as instruções do espaço, ordenando por id.

        Args:
            space_data (dict): O dicionário de metadados mutável do espaço.
        """
        instructions_data = space_data.get('instructions', {})
        
        if isinstance(instructions_data, dict):
            # Chaves diretas que contêm listas com 'id'
            list_keys = ['text_instructions', 'example_question_sqls', 'join_specs']
            for key in list_keys:
                if key in instructions_data and isinstance(instructions_data[key], list):
                    instructions_data[key] = sorted(
                        instructions_data[key],
                        key=lambda item: str(item.get('id', ''))
                    )
            
            # Estrutura aninhada: sql_snippets -> expressions
            sql_snippets = instructions_data.get('sql_snippets', {})
            if isinstance(sql_snippets, dict):
                if 'expressions' in sql_snippets and isinstance(sql_snippets['expressions'], list):
                    sql_snippets['expressions'] = sorted(
                        sql_snippets['expressions'],
                        key=lambda item: str(item.get('id', ''))
                    )

    def _correct_questions(self, space_data: dict) -> None:
        """
        Extrai e formata as questões comuns do espaço, ordenando por id.

        Args:
            space_data (dict): O dicionário de metadados mutável do espaço.
        """
        config_data = space_data.get('config', {})
        if isinstance(config_data, dict):
            if 'sample_questions' in config_data and isinstance(config_data['sample_questions'], list):
                config_data['sample_questions'] = sorted(
                    config_data['sample_questions'],
                    key=lambda item: str(item.get('id', ''))
                )

    def _correct_columns(self, space_data: dict) -> None:
        """
        Ordena as configurações de colunas (column_configs) de cada tabela
        alfanumericamente pelo nome da coluna (column_name).

        Args:
            space_data (dict): O dicionário de metadados mutável do espaço.
        """
        if 'data_sources' in space_data:
            tables_lists = []
            
            # Coleta as listas de tabelas dependendo da estrutura de data_sources
            if isinstance(space_data['data_sources'], dict):
                if 'tables' in space_data['data_sources']:
                    tables_lists.append(space_data['data_sources']['tables'])
            elif isinstance(space_data['data_sources'], list):
                for data_source in space_data['data_sources']:
                    if isinstance(data_source, dict) and 'tables' in data_source:
                        tables_lists.append(data_source['tables'])
            
            # Itera sobre todas as tabelas encontradas e ordena column_configs
            for tables in tables_lists:
                if isinstance(tables, list):
                    for table in tables:
                        if isinstance(table, dict) and 'column_configs' in table:
                            if isinstance(table['column_configs'], list):
                                table['column_configs'] = sorted(
                                    table['column_configs'],
                                    key=lambda c: str(c.get('column_name', ''))
                                )

    @property
    def serialized_space(self) -> str:
        """
        Extrai e formata os dados do espaço, ordenando as entidades internas.

        Realiza uma cópia profunda dos dados para evitar a mutação do dicionário
        de metadados original. As tabelas, instruções e questões de exemplo
        são ordenadas alfanumericamente.

        Returns:
            str: O dicionário 'serialized_space' processado e convertido para JSON (string).
        """
        space_data = copy.deepcopy(self.raw_serialized_space)
        
        self._correct_data_sources(space_data)
        self._correct_columns(space_data)
        self._correct_instructions(space_data)
        self._correct_questions(space_data)

        return json.dumps(space_data)

class GenieCreator:
    """
    Gerenciador para criação e atualização em massa de espaços Genie via Databricks WorkspaceClient.
    
    Esta classe permite enfileirar metadados de espaços Genie e processá-los
    de forma otimizada, garantindo que espaços existentes sejam atualizados
    e novos espaços sejam criados sem redundância de chamadas à API.
    """

    def __init__(self, warehouse_id: str, metadata_list: list[GenieMetadata] | None = None):
        """
        Inicializa o GenieCreator.

        Args:
            warehouse_id (str): O ID do SQL Warehouse onde os Genies serão executados.
            metadata_list (Optional[list[dict]]): Lista opcional contendo os metadados iniciais dos espaços.

        Raises:
            Exception: Se o warehouse_id não for fornecido ou for vazio.
        """
        if not warehouse_id:
            raise Exception("The SQL warehouse ID is required")
        
        self.warehouse_id = warehouse_id
        self.metadata_list = metadata_list if metadata_list is not None else []
        self.workspace_client = WorkspaceClient()

    def add_metadata(self, list_or_unique_metadata: GenieMetadata | list[GenieMetadata]) -> None:
        """
        Adiciona novos metadados à fila de processamento.

        Args:
            list_or_unique_metadata (GenieMetadata | list[GenieMetadata]): Um único dicionário de metadados 
                ou uma lista de dicionários para serem adicionados à fila.
        """
        if isinstance(list_or_unique_metadata, list):
            self.metadata_list.extend(list_or_unique_metadata)
        else:
            self.metadata_list.append(list_or_unique_metadata)

    def create_genie(self, metadata: GenieMetadata) -> tuple[str, GenieSpace]:
        """
        Cria um novo espaço Genie na API.

        Args:
            metadata (GenieMetadata): Metadados contendo 'title', 'description' e 'serialized_space'.

        Returns:
            tuple[str, GenieSpace]: Uma tupla contendo a mensagem de sucesso e o objeto do espaço criado.
        """
        if metadata.parent_path:
            # Creates all folders if they don't exist
            self.workspace_client.workspace.mkdirs(path=metadata.parent_path)

            genie = self.workspace_client.genie.create_space(
                warehouse_id=self.warehouse_id,
                description=metadata.description,
                title=metadata.title,
                serialized_space=metadata.serialized_space,
                parent_path=metadata.parent_path
            )
        else:
            genie = self.workspace_client.genie.create_space(
                    warehouse_id=self.warehouse_id,
                    description=metadata.description,
                    title=metadata.title,
                    serialized_space=metadata.serialized_space
                )

        return f"O genie {genie.title} foi criado com sucesso!", genie

    def update_genie(self, metadata: GenieMetadata, space_id: str) -> tuple[str, GenieSpace]:
        """
        Atualiza um espaço Genie existente na API.

        Args:
            metadata (GenieMetadata): Metadados contendo as novas informações para o espaço.
            space_id (str): O identificador único do espaço que será atualizado.

        Returns:
            tuple[str, GenieSpace]: Uma tupla contendo a mensagem de sucesso e o objeto do espaço atualizado.
        """
        genie = self.workspace_client.genie.update_space(
            space_id=space_id,
            serialized_space=metadata.serialized_space,
            description=metadata.description
        )

        return f"O genie {genie.title} foi atualizado com sucesso!", genie

    def create_or_update_genie_generator(self):
        """
        Gerador iterativo para o processamento em lote dos espaços.

        Mapeia os espaços existentes e decide, para cada item na fila de metadados,
        se deve chamar a função de criação ou de atualização.

        Yields:
            tuple[GenieSpace, str]: O objeto do espaço (criado/atualizado) e sua respectiva mensagem de status.
        """
        spaces_map = get_spaces_map(self.workspace_client)
        
        for metadata in self.metadata_list:
            # Busca se o espaço já existe
            space_id = spaces_map.get(metadata.title)

            if space_id is not None:
                status, genie = self.update_genie(metadata, space_id)
            else:
                status, genie = self.create_genie(metadata)

            yield genie, status

    def create_or_update_all_genies(self) -> None:
        """
        Executa o processo de criação ou atualização para todos os itens da fila de uma só vez.
        """
        print(f"Iniciando processamento de {len(self.metadata_list)} itens...")
        for genie, status in self.create_or_update_genie_generator():
            print(status)
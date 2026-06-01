import datetime as dt

from services.google.client import GoogleClient
from automations_config.tests_config import AUTOMATION_TESTS_FOLDER_ID, DOCS_TEMPLATE_ID


def run(client: GoogleClient) -> None:

    template_copy = client.drive.copy_file(file_id=DOCS_TEMPLATE_ID, new_name=f"Teste Entrevista - {dt.datetime.now()}")

    client.docs.replace_text(
        document_id=template_copy.id,
        replacements={
            "{{NOME_CANDIDATO}}": "Simon Silva",
            "{{SETORES_PREFERENCIA}}": "Jurídico-Financeiro, Gestão de Pessoas",
            "{{NOMES_AVALIADORES}}": "Silvia dos Santos, Simone Santana",
            "{{AVALIACAO_DINAMICA}}": "Bom",
            "{{DESCRICAO_DINAMICA}}": "Falou pouco com o grupo durante a dinâmica;\nDeu ideias muito boas para estruturar a solução;\nTravou um pouco na apresentação."
        }
    )

    client.drive.move_file_to_folder(file_id=template_copy.id, folder_id=AUTOMATION_TESTS_FOLDER_ID)
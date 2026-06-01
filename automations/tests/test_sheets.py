import datetime as dt

from services.google.client import GoogleClient
from automations_config.tests_config import AUTOMATION_TESTS_FOLDER_ID

def run(client: GoogleClient) -> None:

    spreadsheet = client.sheets.create_spreadsheet(f"Planilha Teste - {dt.datetime.now()}")

    client.sheets.write_range(
        spreadsheet_id=spreadsheet.id,
        range_name="A1:D3",
        values=[
            ["Nome", "Avaliação na Dinâmica", "Setor 1", "Setor 2"],
            ["Simon Silva", "Bom", "Jurídico-Financeiro", "Gestão de Pessoas"],
            ["Sinderella Souza", "Ótimo", "Gestão de Pessoas", "Comercial"]
        ]
    )

    client.drive.move_file_to_folder(file_id=spreadsheet.id, folder_id=AUTOMATION_TESTS_FOLDER_ID)
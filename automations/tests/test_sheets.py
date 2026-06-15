import datetime as dt

from services.google.client import GoogleClient
from automations_config.tests_config import AUTOMATION_TESTS_FOLDER_ID

def run(client: GoogleClient) -> None:
    spreadsheet = client.sheets.create_spreadsheet(
        title=f"Planilha Teste - {dt.datetime.now()}",
        sheet_names=["Página 1", "Página 2"]
    )

    client.sheets.write_range(
        spreadsheet_id=spreadsheet.id,
        range_name="Página 1!A1:D3",
        values=[
            ["Nome", "Avaliação na Dinâmica", "Setor 1", "Setor 2"],
            ["Simon Silva", "Bom", "Jurídico-Financeiro", "Gestão de Pessoas"],
            ["Sinderella Souza", "Ótimo", "Gestão de Pessoas", "Comercial"]
        ]
    )
    client.sheets.write_range(
        spreadsheet_id=spreadsheet.id,
        range_name="Página 2!A1:D2",
        values=[
            ["Nome", "Avaliação na Dinâmica", "Setor 1", "Setor 2"],
            ["Simon Silva", "Bom", "Jurídico-Financeiro", "Gestão de Pessoas"]
        ]
    )

    client.drive.move_file_to_folder(file_id=spreadsheet.id, folder_id=AUTOMATION_TESTS_FOLDER_ID)
from services.google.client import GoogleClient


from automations_config.interview_docs_generator_config import (
    INTERVIEW_TEMPLATE_DOCS_ID,
    CANDIDATES_INFORMATION_SPREADSHEET_ID,
    CURRENT_RECRUITMENT_PROCESS_INTERVIEW_FOLDER_ID
)
from automations.utils.list_operations import (
    convert_matrix_to_list_dict, 
    sort_list_dicts,
    filter_list_dict 
)

def get_candidates_approved_in_st_stage(client:GoogleClient) -> list[dict]:
    all_candidates_matrix = client.sheets.read_range(
        spreadsheet_id=CANDIDATES_INFORMATION_SPREADSHEET_ID,
        range_name="Report!A:T"
    )

    all_candidates_matrix[0][2] = "Apresentação Pessoal"
    all_candidates_matrix[0][9] = "Interesse no Núcleo de Vendas 1"
    all_candidates_matrix[0][10] = "Interesse no Núcleo de Vendas 2"
    all_candidates_matrix[0][11] = "Interesse no Núcleo de Marketing 1"
    all_candidates_matrix[0][12] = "Interesse no Núcleo de Marketing 2"

    all_candidates = convert_matrix_to_list_dict(
        matrix=all_candidates_matrix
    )

    approved_candidates = filter_list_dict(
        list_dict=all_candidates,
        key="Vai pra Entrevista",
        value="Sim"
    )

    for c in approved_candidates:
        if c["Interesse no Núcleo de Vendas 1"] == '' and c["Interesse no Núcleo de Vendas 2"] != '':
            c["Interesse no Núcleo de Vendas 1"] = c["Interesse no Núcleo de Vendas 2"]
        elif c["Interesse no Núcleo de Vendas 1"] != '' and c["Interesse no Núcleo de Vendas 2"] == '':
            c["Interesse no Núcleo de Vendas 2"] = c["Interesse no Núcleo de Vendas 1"]
        elif c["Interesse no Núcleo de Vendas 1"] != c["Interesse no Núcleo de Vendas 2"]:
            c["Interesse no Núcleo de Vendas 1"] = "Divergência! Consulte o pipefy ou um membro de GP"
            c["Interesse no Núcleo de Vendas 2"] = "Divergência! Consulte o pipefy ou um membro de GP"

        if c["Interesse no Núcleo de Marketing 1"] == '' and c["Interesse no Núcleo de Marketing 2"] != '':
            c["Interesse no Núcleo de Marketing 1"] = c["Interesse no Núcleo de Marketing 2"]
        elif c["Interesse no Núcleo de Marketing 1"] != '' and c["Interesse no Núcleo de Marketing 2"] == '':
            c["Interesse no Núcleo de Marketing 2"] = c["Interesse no Núcleo de Marketing 1"]
        elif c["Interesse no Núcleo de Marketing 1"] != c["Interesse no Núcleo de Marketing 2"]:
            c["Interesse no Núcleo de Marketing 1"] = "Divergência! Consulte o pipefy ou um membro de GP"
            c["Interesse no Núcleo de Marketing 2"] = "Divergência! Consulte o pipefy ou um membro de GP"

    return approved_candidates

def create_candidate_interview_docs(client:GoogleClient, candidate:dict):
    template_copy = client.drive.copy_file(
        file_id=INTERVIEW_TEMPLATE_DOCS_ID,
        new_name=f"Entrevista {candidate['Nome completo']}"
    )
    client.docs.replace_text(
        document_id=template_copy.id,
        replacements={
            #"{{ENTREVISTADORES}}": 
            "{{NOME_CANDIADATO}}": candidate["Nome completo"],
            "{{EMAIL_CANDIDATO}}": candidate["Email"],
            "{{TELEGRAM_CANDIDATO}}": candidate["Whatsapp"],
            "{{WHATSAPP_CANDIDATO}}": candidate["Telegram"],
            "{{PREFERENCIAS_SETORES}}": (
                f"1ª opção: {candidate['Primeira opção de setor']}\n" + 
                f"2ª opção: {candidate['Segunda opção de setor']}"
            ),
            "{{PREFERENCIAS_NUCLEOS_COMERCIAL}}": (
                f"Marketing: {candidate['Interesse no Núcleo de Marketing 1']}\n" + 
                f"Vendas: {candidate['Interesse no Núcleo de Vendas 1']}"
            ),
            "{{PREFERENCIAS_NUCLEOS_PROJETOS}}": (
                f"Criação: {candidate['Interesse no Núcleo de Criação']}\n" +
                f"Front-End: {candidate['Interesse no Núcleo de Front-End']}\n" +
                f"Back-End: {candidate['Interesse no Núcleo de Back-End']}\n" +
                f"Dados: {candidate['Interesse no Núcleo de Dados']}"
            ),
            "{{DESCRIACAO_PIPEFY}}": candidate["Apresentação Pessoal"],
            #"{{AVALIADORES_DINAMICA}}": candidate[""],
            "{{DESESEMPENHO_DINAMICA}}": (
                f"Avaliação geral: {candidate['Avaliação']}\n" +
                f"{candidate['Descrição da Dinâmica']}"
            )
        }
    )
    client.drive.move_file_to_folder(
        file_id=template_copy.id,
        folder_id=CURRENT_RECRUITMENT_PROCESS_INTERVIEW_FOLDER_ID
    )

def terminal_interview_docs_generator():
    client = GoogleClient()
    approved_candidates = get_candidates_approved_in_st_stage(client)

    for candidate in approved_candidates:
        create_candidate_interview_docs(
            client=client,
            candidate=candidate
        )
        

if __name__ == "__main__":
    terminal_interview_docs_generator()
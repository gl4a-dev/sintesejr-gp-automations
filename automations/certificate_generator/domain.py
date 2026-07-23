from datetime import datetime
from time import sleep

from services.google.client import GoogleClient
from models.gmail import EmailAttachment

from automations_config.certificate_generator_config import (
    MEMBER_ROLE_MANAGEMENT_SPREADSHEET_ID, 
    TERMINED_CERTIFICATE_TEMPLATE_DOCS_WITH_CPF_ID,
    TERMINED_CERTIFICATE_TEMPLATE_DOCS_NO_CPF_ID
)
from automations.utils.list_operations import (
    convert_matrix_to_list_dict, 
    sort_list_dicts,
    filter_list_dict 
)

def get_terminated_members(client:GoogleClient) -> list[dict]:
    terminated_members = client.sheets.read_range(
        spreadsheet_id=MEMBER_ROLE_MANAGEMENT_SPREADSHEET_ID,
        range_name="Membros Desligados!A:T"
    )
    terminated_members_list_dict = convert_matrix_to_list_dict(
        matrix=terminated_members
    )
    return sort_list_dicts(
        list_dict=terminated_members_list_dict,
        key="Data de Desligamento",
        ascending=False
    )

def show_terminated_members_names(terminated_members:list[dict], top:int) -> None:
    print("-"*40)
    print(f"Últimos {min(top, terminated_members.__len__())} membros desligados")

    for member in terminated_members[:top]:
        print(f"{member['indice']} - {member['Nome']}")

    print("-"*40)

def ask_for_member_index() -> int:
    index = input("Digite o indice do membro que deseja emitir o certificado: ")
    print("-"*40)
    return int(index)

def filter_terminated_member_by_index(terminated_members:list[dict], member_index:int) -> dict:
    return filter_list_dict(
        list_dict=terminated_members,
        key="indice",
        value=member_index
    )[0]

def get_terminated_member_role_history(client:GoogleClient, member_name:str) -> list[dict]:
    members_role_history = client.sheets.read_range(
        spreadsheet_id=MEMBER_ROLE_MANAGEMENT_SPREADSHEET_ID,
        range_name="Gestão de Cargos!A:F"
    )
    members_role_history_list_dict = convert_matrix_to_list_dict(
        matrix=members_role_history
    )
    member_role_history = filter_list_dict(
        list_dict=members_role_history_list_dict,
        key="Nome do Membro",
        value=member_name
    )
    return sort_list_dicts(
        list_dict=member_role_history,
        key="Data de Início",
        ascending=True
    )

def format_role_name(role_name:str) -> str:
    formatter = {}
    formatter["Trainee"] = "Trainee"
    formatter["Associado"] = "Associado(a)"
    formatter["Coordenador"] = "Coordenador(a)"
    formatter["Diretor"] = "Diretor(a)"
    formatter["Vice-Presidente e Diretor"] = "Vice-Presidente e Diretor(a)"

    return formatter[role_name]


def format_member_roles(roles:list[dict]) -> str:
    text = ""
    for role in roles:
        text += f"De {datetime.strptime(role['Data de Início'], '%Y-%m-%d').strftime('%d/%m/%Y')} "
        text += f"até {datetime.strptime(role['Data de Fim'], '%Y-%m-%d').strftime('%d/%m/%Y')}: "
        text += f"{format_role_name(role['Cargo'])} de {role['Núcleo ou Setor']}\n"

    return text
        

def show_member_info(personal_info:dict, roles:list[dict]) -> None:
    print("Informações do membro que desaja emitir o certificado:")

    print(f"Nome: {personal_info['Nome']}")
    print(f"CPF: {personal_info['CPF']}")
    print(f"Email USP: {personal_info['E-mail']}\n")
    print(format_member_roles(roles))

    print("-"*40)

def ask_for_confirmation() -> bool:
    confirmation = str(input("Digite 's' para confirmar ou outra para não: "))
    print(40*"-")
    if confirmation == 's':
        return True
    else:
        return False

def terminal_certificate_generator():
    client = GoogleClient()

    terminated_members = get_terminated_members(client)

    show_terminated_members_names(
        terminated_members=terminated_members,
        top=10
    )
    index = ask_for_member_index()

    member = filter_terminated_member_by_index(
        terminated_members=terminated_members,
        member_index=index
    )
    if member == None:
        print("Nenhum membro encontrado.\nEncerrando o programa.")
        return
    
    roles = get_terminated_member_role_history(client, member["Nome"])
    show_member_info(
        personal_info=member,
        roles=roles
    )

    confirmation = ask_for_confirmation()
    if confirmation == False:
        print("Membro não confirmado.\nEncerrando o programa.")
        return
    
    certificate_with_cpf_copy = client.drive.copy_file(
        file_id=TERMINED_CERTIFICATE_TEMPLATE_DOCS_WITH_CPF_ID,
        new_name=f"Certificado de Conclusão (com CPF) - {member['Nome']}"
    )
    client.docs.replace_text(
        document_id=certificate_with_cpf_copy.id,
        replacements={
            "{{NOME}}": member['Nome'],
            "{{CPF}}": member['CPF'],
            "{{HORAS}}": member['Horas Acumuladas'],
            "{{DATA_ENTRADA}}": datetime.strptime(member['Data de Entrada'], "%Y-%m-%d").strftime("%d/%m/%Y"),
            "{{DATA_DESLIGAMENTO}}": datetime.strptime(member['Data de Desligamento'], "%Y-%m-%d").strftime("%d/%m/%Y")
        }
    )
    certificate_with_cpf_pdf_bytes = client.drive.export_file(
        file_id=certificate_with_cpf_copy.id,
        mime_type="application/pdf"
    )

    certificate_no_cpf_copy = client.drive.copy_file(
        file_id=TERMINED_CERTIFICATE_TEMPLATE_DOCS_NO_CPF_ID,
        new_name=f"Certificado de Conclusão (sem CPF) - {member['Nome']}"
    )
    client.docs.replace_text(
        document_id=certificate_no_cpf_copy.id,
        replacements={
            "{{NOME}}": member['Nome'],
            "{{HORAS}}": member['Horas Acumuladas'],
            "{{DATA_ENTRADA}}": datetime.strptime(member['Data de Entrada'], "%Y-%m-%d").strftime("%d/%m/%Y"),
            "{{DATA_DESLIGAMENTO}}": datetime.strptime(member['Data de Desligamento'], "%Y-%m-%d").strftime("%d/%m/%Y")
        }
    )
    certificate_no_cpf_pdf_bytes = client.drive.export_file(
        file_id=certificate_no_cpf_copy.id,
        mime_type="application/pdf"
    )

    print("Certificados gerados!")

    client.gmail.send_email(
        to=[member['E-mail']],
        subject="Certificado de Desligamento",
        body=f"<h1>Certificado de Desligamento de {member['Nome']}</h1><p>Segue em anexo seu certificado</p>",
        html=True,
        attachments=[
            EmailAttachment(
                filename=f"Certificado de Desligamento - {member['Nome']}.pdf",
                content=certificate_with_cpf_pdf_bytes,
                mime_type="application/pdf"
            ),
            EmailAttachment(
                filename=f"Certificado de Desligamento (sem CPF) - {member['Nome']}.pdf",
                content=certificate_no_cpf_pdf_bytes,
                mime_type="application/pdf"
            )
        ]
    )

    print("Email enviado com sucesso!")

    client.drive.delete_file(
        file_id=certificate_with_cpf_copy.id
    )
    client.drive.delete_file(
        file_id=certificate_no_cpf_copy.id
    )

    print("Cópias temporárias deletadas!")
    
if __name__ == "__main__":
    terminal_certificate_generator()


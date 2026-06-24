from datetime import date, datetime

from services.google.client import GoogleClient
from models.admin import CreatedGoogleUser

from automations_config.certificate_generator_config import MEMBER_ROLE_MANAGEMENT_SPREADSHEET_ID
from automations.utils.list_operations import convert_matrix_to_list_dict


def get_todays_semester() -> date:
    today = date.today()

    if today.month <= 6:
        return date(today.year, 1, 1)
    else:
        return date(today.year, 7, 1)

def get_new_members(client:GoogleClient) -> list[dict]:
    members = client.sheets.read_range(
        spreadsheet_id=MEMBER_ROLE_MANAGEMENT_SPREADSHEET_ID,
        range_name="Membros Ativos!A:T"
    )
    members_list_dict = convert_matrix_to_list_dict(
        matrix=members
    )
    return [
        member for member in members_list_dict 
        if datetime.strptime(member["Data de Entrada"], "%Y-%m-%d").date() >= get_todays_semester()
    ]

def show_members_information(members:list[dict]):
    print("-"*40)
    print(f"Últimos ingressantes desde {get_todays_semester().strftime('%d/%m/%Y')}")
    for member in members:
        print(f"{member['Nome']}, {member['E-mail']}, Email Síntese: {member['Email Síntese']}")
    print("-"*40)

def ask_for_confirmation() -> bool:
    confirmation = str(input("Digite 's' para confirmar a criação de emails ou outra tecla para não: "))
    print(40*"-")
    if confirmation == 's':
        return True
    else:
        return False

def create_account(client:GoogleClient, member:dict) -> CreatedGoogleUser:
    first_name, last_name = member['Nome'].split(" ", 1)
    return client.admin.create_user(
        first_name=first_name,
        last_name=last_name,
        primary_email=member["Email Síntese"],
        recovery_email=member["E-mail"]
    )

def send_first_access_email(client:GoogleClient, user:CreatedGoogleUser):
    client.gmail.send_email(
        to=[user.recovery_email],
        subject="Criação da conta da Síntese Jr.",
        body=f"<p>Sua conta da Google no domínio @sintesejr.com.br foi criada. Nela você terá acesso às ferramentas do Google Workspace em um espaço compartilhado com os outros membros da EJ.</p><p>Para acessá-la, você deve fazer login com o email e a senha temporária abaixo:</p><br><p><b>Email:</b> {user.primary_email}</p><p><b>Senha temporária:</b> {user.temporary_password}</p>",
        html=True
    )

def terminal_account_creator():
    client = GoogleClient()

    new_members = get_new_members(client)
    show_members_information(new_members)

    confirmation = ask_for_confirmation()
    if confirmation == False:
        print("Dados não confirmados.\nEncerrando o programa.")
        return

    for member in new_members:
        user = create_account(client, member)
        send_first_access_email(client, user)

    print("Contas criadas e emails com instruções de acesso enviados!")

if __name__ == "__main__":
    terminal_account_creator()

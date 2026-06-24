from datetime import datetime

def convert_matrix_to_list_dict(matrix:list[list[str]]) -> list[dict]:
    header_fields = matrix.pop(0)

    terminated_members_array_dicts = []
    for member_fields in matrix:
        member_dict = {}

        for i in range(header_fields.__len__()):
            if header_fields[i].lower().__contains__("data") and member_fields[i] != '':
                member_dict[header_fields[i]] = datetime.strptime(member_fields[i], "%d/%m/%Y").strftime("%Y-%m-%d")
            else:
                member_dict[header_fields[i]] = member_fields[i]

        terminated_members_array_dicts.append(member_dict)

    return terminated_members_array_dicts

def filter_list_dict(list_dict:list[dict], key:str, value:str) -> list[dict]:
    return [info_dict for info_dict in list_dict if info_dict[key] == value]

def sort_list_dicts(list_dict:list[dict], key:str, ascending:bool) -> list[dict]:
    sorted_list_dict = sorted(
        list_dict,
        key=lambda member: member[key],
        reverse=not ascending
    )

    for i, member in enumerate(sorted_list_dict):
        member["indice"] = i

    return sorted_list_dict
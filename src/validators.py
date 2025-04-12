import re


def is_required(value):
    if value:
        return {"ok": True, "value": value}
    return {"ok": False, "error": "This field is required."}


def is_email(value):
    if "@" in value and "." in value:
        return {"ok": True, "value": value}
    return {"ok": False, "error": "Invalid email address."}


def is_host(value):
    if "." not in value:
        return {"ok": False, "error": "Invalid host"}
    if "http" in value:
        return {"ok": False, "error": "Host should not contain protocol. Remove http from host."}

    return {"ok": True, "value": value}


def is_doi(doi):
    pattern = r"[0-9]{2}\.[0-9]{4}\/[0-9a-zA-Z:.]+(\/[0-9a-zA-Z:.]+)?"

    result = re.search(pattern, doi)

    if result:
        return True
    return False


def get_invalid_dois(doi_list: list) -> list:
    invalid_doi_list = []

    for doi in doi_list:
        if not is_doi(doi):
            invalid_doi_list.append(doi)
    return invalid_doi_list


def chain_validators(value, *validators):
    for validator in validators:
        result = validator(value)
        if not result["ok"]:
            return result
    return {"ok": True, "value": value}


def validate_form(data):
    return {
        "email": chain_validators(data.get("email"), is_required, is_email),
        "resolver": chain_validators(data.get("resolving_host"), is_required, is_host),
    }


def get_errors(validated_data):
    return {field: result["error"] for field, result in validated_data.items() if not result["ok"]}

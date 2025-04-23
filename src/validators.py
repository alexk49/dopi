import re

from helpers import get_list_from_str


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


def is_doi(doi: str) -> bool:
    """
    Checks DOI against CrossRef recommended regex:

    https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    """
    doi_regex = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
    return bool(re.search(doi_regex, doi.strip()))


def get_invalid_dois(doi_list: list[str]) -> list[str]:
    return [doi for doi in doi_list if not is_doi(doi)]


def validate_dois(dois_text):
    dois_list = get_list_from_str(dois_text)
    print(dois_list)
    print(type(dois_list))
    invalid_dois = get_invalid_dois(dois_list)

    if invalid_dois:
        return {"ok": False, "error": f"Invalid DOIs given: {', '.join(invalid_dois)}"}

    return {"ok": True, "value": dois_list}


def chain_validators(value, *validators) -> dict:
    """
    Called by validate_form and used to run
    all required validation functions on form value
    """
    for validator in validators:
        result = validator(value)
        if not result["ok"]:
            return result
    print(f"VALIDATING VALUE: {value}")
    print(f"RESULTING VALUE: {result['value']}")
    return {"ok": True, "value": result["value"]}


def is_valid_input_method(value):
    if value in {"dois_text", "dois_upload"}:
        return {"ok": True, "value": value}
    return {"ok": False, "error": "Invalid DOI input method selected."}


def validate_form(data) -> dict:
    """
    Runs all form validation and returns dict of results

    Successful validation might look like:

    {'email': {'ok': True, 'value': 'someone@email.com'}, 'resolver': {'ok': True, 'value': 'anotherexample.com'}, 'dois_text': {'ok': True, 'value': 'doi-value'}}
    """
    results = {
        "input_method": chain_validators(data.get("input_method"), is_required, is_valid_input_method),
        "email": chain_validators(data.get("email"), is_required, is_email),
        "resolver": chain_validators(data.get("resolving_host"), is_required, is_host),
    }

    if results["input_method"]["ok"] and results["input_method"]["value"] == "dois_text":
        results["dois"] = chain_validators(data.get("dois_text"), is_required, validate_dois)
    return results


def get_errors(validated_data):
    """
    Filter through results of validate_form dict
    to find any errors

    Results might look like:
    {'email': {'ok': True, 'value': 'someone@email.com'}, 'resolver': {'ok': True, 'value': 'anotherexample.com'}, 'dois_text': {'ok': False, 'error': 'Invalid DOIs given: fake-doi'}}

    Checks for ok: Fale and returns error messages
    """
    return {field: result["error"] for field, result in validated_data.items() if not result["ok"]}

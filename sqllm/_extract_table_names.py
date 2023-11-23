# ref: https://github.com/andialbrecht/sqlparse/issues/157

import itertools

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword


def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == "SELECT":
            return True
    return False


def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if item.is_group:
            for x in extract_from_part(item):
                yield x
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword and item.value.upper() in [
                "ORDER",
                "GROUP",
                "BY",
                "HAVING",
                "GROUP BY",
            ]:
                from_seen = False
                StopIteration
            else:
                yield item
        if item.ttype is Keyword and item.value.upper() == "FROM":
            from_seen = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                value = identifier.value.replace('"', "").lower()
                yield value
        elif isinstance(item, Identifier):
            value = item.value.replace('"', "").lower()
            yield value


def extract_tables(sql):
    # let's handle multiple statements in one sql string
    extracted_tables = []
    statements = list(sqlparse.parse(sql))
    for statement in statements:
        if statement.get_type() != "UNKNOWN":
            stream = extract_from_part(statement)
            extracted_tables.append(set(list(extract_table_identifiers(stream))))
    return list(itertools.chain(*extracted_tables))

from __future__ import annotations

import re
import runpy
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections


ROOT = Path(__file__).resolve().parents[3]
MERMAID_PATH = ROOT / "docs" / "db_er_diagram.mmd"
EXPLORER_GENERATOR = ROOT / "docs" / "er_explorer" / "generate_er_explorer.py"


FIELD_TYPE_MAP = {
    "AutoField": "int",
    "BigAutoField": "bigint",
    "BigIntegerField": "bigint",
    "BinaryField": "binary",
    "BooleanField": "boolean",
    "CharField": "varchar",
    "DateField": "date",
    "DateTimeField": "datetime",
    "DecimalField": "decimal",
    "DurationField": "duration",
    "EmailField": "varchar",
    "FileField": "varchar",
    "FloatField": "float",
    "IntegerField": "int",
    "JSONField": "json",
    "PositiveBigIntegerField": "bigint",
    "PositiveIntegerField": "int",
    "PositiveSmallIntegerField": "int",
    "SlugField": "varchar",
    "SmallAutoField": "int",
    "SmallIntegerField": "int",
    "TextField": "text",
    "TimeField": "time",
    "UUIDField": "uuid",
}


def mermaid_identifier(value: str) -> str:
    cleaned = re.sub(r"\W+", "_", value.strip())
    if not cleaned:
        return "unnamed"
    if cleaned[0].isdigit():
        return f"t_{cleaned}"
    return cleaned


def mermaid_type(connection, description) -> str:
    try:
        django_type = connection.introspection.get_field_type(description.type_code, description)
    except Exception:
        django_type = str(getattr(description, "type_code", "unknown"))
    mapped = FIELD_TYPE_MAP.get(django_type, django_type)
    mapped = re.sub(r"\W+", "_", mapped).strip("_").lower()
    return mapped or "unknown"


def table_names(connection, cursor) -> list[str]:
    tables = []
    for table in connection.introspection.get_table_list(cursor):
        table_type = getattr(table, "type", None)
        if table_type in (None, "t"):
            tables.append(table.name)
    return sorted(tables)


def build_mermaid_from_database(alias: str) -> tuple[int, int]:
    connection = connections[alias]
    tables: dict[str, dict] = {}
    relationships = []

    with connection.cursor() as cursor:
        names = table_names(connection, cursor)
        name_map = {name: mermaid_identifier(name) for name in names}

        for table_name in names:
            constraints = connection.introspection.get_constraints(cursor, table_name)
            primary_key_columns: set[str] = set()
            unique_columns: set[str] = set()
            foreign_key_columns: set[str] = set()

            for constraint in constraints.values():
                columns = tuple(constraint.get("columns") or ())
                if constraint.get("primary_key"):
                    primary_key_columns.update(columns)
                if constraint.get("unique") and len(columns) == 1:
                    unique_columns.update(columns)

                foreign_key = constraint.get("foreign_key")
                if foreign_key and columns:
                    target_table, _target_column = foreign_key
                    foreign_key_columns.update(columns)
                    relationships.append(
                        {
                            "src": name_map.get(target_table, mermaid_identifier(target_table)),
                            "dst": name_map[table_name],
                            "label": columns[0],
                        }
                    )

            fields = []
            for description in connection.introspection.get_table_description(cursor, table_name):
                column_name = description.name
                tags = []
                if column_name in primary_key_columns:
                    tags.append("PK")
                if column_name in foreign_key_columns:
                    tags.append("FK")
                if column_name in unique_columns and column_name not in primary_key_columns:
                    tags.append("UK")

                notes = []
                if getattr(description, "null_ok", False):
                    notes.append("nullable")

                fields.append(
                    {
                        "name": mermaid_identifier(column_name),
                        "type": mermaid_type(connection, description),
                        "tags": tags,
                        "notes": notes,
                    }
                )

            tables[table_name] = {"name": name_map[table_name], "fields": fields}

    lines = [
        "---",
        "title: Factory App Database ER Diagram",
        "---",
        "erDiagram",
    ]

    for table_name in sorted(tables):
        table = tables[table_name]
        lines.append(f"    {table['name']} {{")
        for field in table["fields"]:
            tag_part = f" {' '.join(field['tags'])}" if field["tags"] else ""
            note_part = "".join(f' "{note}"' for note in field["notes"])
            lines.append(f"        {field['type']} {field['name']}{tag_part}{note_part}")
        lines.append("    }")
        lines.append("")

    for relationship in sorted(relationships, key=lambda item: (item["src"], item["dst"], item["label"])):
        label = str(relationship["label"]).replace('"', "'")
        lines.append(f'    {relationship["src"]} ||--o{{ {relationship["dst"]} : "{label}"')

    MERMAID_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(tables), len(relationships)


class Command(BaseCommand):
    help = "Refresh docs/db_er_diagram.mmd and docs/er_explorer from the configured Django database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=f'Database alias to introspect. Defaults to "{DEFAULT_DB_ALIAS}".',
        )

    def handle(self, *args, **options):
        alias = options["database"]
        if alias not in connections:
            raise CommandError(f'Unknown database alias "{alias}".')
        if not EXPLORER_GENERATOR.exists():
            raise CommandError(f"Missing ER explorer generator: {EXPLORER_GENERATOR}")

        table_count, relationship_count = build_mermaid_from_database(alias)
        runpy.run_path(str(EXPLORER_GENERATOR), run_name="__main__")

        self.stdout.write(
            self.style.SUCCESS(
                f"Refreshed ER explorer from database '{alias}': "
                f"{table_count} tables, {relationship_count} relationships."
            )
        )

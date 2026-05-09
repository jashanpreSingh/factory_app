"""Generate database schema and ER documentation from Django models."""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
SCHEMA_DOC = DOCS_DIR / "database_schema.md"
ER_DOC = DOCS_DIR / "er_model.md"
ER_MERMAID = DOCS_DIR / "er_model.mmd"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


VALID_BOOL_STRINGS = {"1", "0", "true", "false", "yes", "no", "on", "off"}


def configure_django():
    """Load Django without relying on a valid DEBUG value in the local .env."""
    debug_value = os.environ.get("DEBUG")
    if debug_value is None or debug_value.lower() not in VALID_BOOL_STRINGS:
        os.environ["DEBUG"] = "False"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()


def field_type(field) -> str:
    """Return a compact, useful Django type description."""
    type_name = field.get_internal_type()
    parts: list[str] = []

    max_length = getattr(field, "max_length", None)
    if max_length:
        parts.append(f"max_length={max_length}")

    max_digits = getattr(field, "max_digits", None)
    decimal_places = getattr(field, "decimal_places", None)
    if max_digits is not None:
        parts.append(f"max_digits={max_digits}")
    if decimal_places is not None:
        parts.append(f"decimal_places={decimal_places}")

    if parts:
        return f"{type_name}({', '.join(parts)})"
    return type_name


def mermaid_type(field) -> str:
    """Map Django field types to Mermaid-friendly attribute types."""
    type_name = field.get_internal_type()
    mapping = {
        "AutoField": "int",
        "BigAutoField": "bigint",
        "BigIntegerField": "bigint",
        "BooleanField": "boolean",
        "CharField": "varchar",
        "DateField": "date",
        "DateTimeField": "datetime",
        "DecimalField": "decimal",
        "DurationField": "duration",
        "EmailField": "varchar",
        "FileField": "varchar",
        "FloatField": "float",
        "ForeignKey": "bigint",
        "ImageField": "varchar",
        "IntegerField": "int",
        "JSONField": "json",
        "ManyToManyField": "bigint",
        "OneToOneField": "bigint",
        "PositiveIntegerField": "int",
        "PositiveSmallIntegerField": "smallint",
        "SlugField": "varchar",
        "SmallIntegerField": "smallint",
        "TextField": "text",
        "TimeField": "time",
        "UUIDField": "uuid",
    }
    return mapping.get(type_name, type_name.lower())


def relation_target(field) -> str:
    if not getattr(field, "remote_field", None) or not field.remote_field:
        return ""
    remote_model = field.remote_field.model
    if isinstance(remote_model, str):
        return remote_model

    target_field = getattr(field, "target_field", None)
    if target_field is not None:
        return f"{remote_model._meta.db_table}.{target_field.column}"
    return remote_model._meta.db_table


def key_flags(field) -> str:
    flags: list[str] = []
    if getattr(field, "primary_key", False):
        flags.append("PK")
    if getattr(field, "is_relation", False) and getattr(field, "remote_field", None):
        flags.append("FK")
    if getattr(field, "unique", False) and not getattr(field, "primary_key", False):
        flags.append("UNIQUE")
    return ", ".join(flags)


def get_models():
    from django.apps import apps

    models = [
        model
        for model in apps.get_models(include_auto_created=True)
        if model._meta.managed and not model._meta.proxy
    ]
    return sorted(models, key=lambda model: (model._meta.app_label, model._meta.db_table))


def get_unmanaged_models():
    from django.apps import apps

    models = [
        model
        for model in apps.get_models(include_auto_created=True)
        if not model._meta.managed and not model._meta.proxy
    ]
    return sorted(models, key=lambda model: (model._meta.app_label, model.__name__))


def model_fields(model) -> Iterable:
    return list(model._meta.local_fields)


def markdown_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_schema_doc(models, unmanaged_models, relationships) -> str:
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    by_app: dict[str, list] = defaultdict(list)
    for model in models:
        by_app[model._meta.app_label].append(model)

    lines: list[str] = [
        "# Database Schema",
        "",
        f"Generated on: `{generated_on}`",
        "",
        "Source: Django model metadata via `scripts/generate_er_docs.py`.",
        "",
        "Scope: managed Django models plus implicit many-to-many join tables. "
        "Unmanaged permission-only sentinel models are listed separately because "
        "Django does not create database tables for them.",
        "",
        "Related ER files:",
        "",
        "- [er_model.md](er_model.md)",
        "- [er_model.mmd](er_model.mmd)",
        "",
        "## Summary",
        "",
        f"- Managed tables: `{len(models)}`",
        f"- Relationships: `{len(relationships)}`",
        f"- Apps with managed tables: `{len(by_app)}`",
        "",
    ]

    if unmanaged_models:
        lines.extend(
            [
                "## Unmanaged Permission Models",
                "",
                "| App | Model | Declared table name | Note |",
                "| --- | --- | --- | --- |",
            ]
        )
        for model in unmanaged_models:
            lines.append(
                "| "
                f"{markdown_escape(model._meta.app_label)} | "
                f"{markdown_escape(model.__name__)} | "
                f"{markdown_escape(model._meta.db_table)} | "
                "No table is created (`managed = False`) |"
            )
        lines.append("")

    lines.extend(["## Tables And Columns", ""])

    for app_label, app_models in by_app.items():
        lines.extend([f"### {app_label}", ""])
        for model in app_models:
            auto_note = " (implicit join table)" if model._meta.auto_created else ""
            lines.extend(
                [
                    f"#### `{model._meta.db_table}`{auto_note}",
                    "",
                    f"Django model: `{model._meta.label}`",
                    "",
                    "| Column | Model field | Type | Key | Null | Relation |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for field in model_fields(model):
                null_value = "YES" if getattr(field, "null", False) else "NO"
                lines.append(
                    "| "
                    f"`{markdown_escape(field.column)}` | "
                    f"`{markdown_escape(field.name)}` | "
                    f"`{markdown_escape(field_type(field))}` | "
                    f"{markdown_escape(key_flags(field))} | "
                    f"{null_value} | "
                    f"{markdown_escape(relation_target(field))} |"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def collect_relationships(models):
    model_by_table = {model._meta.db_table: model for model in models}
    relationships: list[tuple[str, str, str, str]] = []

    for model in models:
        source = model._meta.db_table
        for field in model_fields(model):
            if not getattr(field, "is_relation", False):
                continue
            if not getattr(field, "remote_field", None):
                continue
            remote_model = field.remote_field.model
            if isinstance(remote_model, str):
                continue
            target = remote_model._meta.db_table
            if target not in model_by_table:
                continue

            relation = "||--o|"
            if field.many_to_one:
                relation = "||--o{"
            elif field.one_to_one and not getattr(field, "null", False):
                relation = "||--||"

            relationships.append((target, relation, source, field.column))

    return sorted(set(relationships))


def render_mermaid(models, relationships) -> str:
    lines: list[str] = ["erDiagram"]

    for model in models:
        lines.append(f"    {model._meta.db_table} {{")
        for field in model_fields(model):
            flags: list[str] = []
            if field.primary_key:
                flags.append("PK")
            elif getattr(field, "is_relation", False) and getattr(field, "remote_field", None):
                flags.append("FK")
            elif field.unique:
                flags.append("UK")

            suffix = f" {' '.join(flags)}" if flags else ""
            lines.append(f"        {mermaid_type(field)} {field.column}{suffix}")
        lines.append("    }")

    for target, relation, source, label in relationships:
        lines.append(f"    {target} {relation} {source} : \"{label}\"")

    return "\n".join(lines) + "\n"


def render_er_doc(mermaid: str, models, relationships) -> str:
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "# ER Model\n\n"
        f"Generated on: `{generated_on}`\n\n"
        "Source: Django model metadata via `scripts/generate_er_docs.py`.\n\n"
        f"- Managed tables: `{len(models)}`\n"
        f"- Relationships: `{len(relationships)}`\n"
        "- Full column inventory: [database_schema.md](database_schema.md)\n"
        "- Raw Mermaid source: [er_model.mmd](er_model.mmd)\n\n"
        "```mermaid\n"
        f"{mermaid}"
        "```\n"
    )


def main() -> None:
    configure_django()
    DOCS_DIR.mkdir(exist_ok=True)

    models = get_models()
    unmanaged_models = get_unmanaged_models()
    relationships = collect_relationships(models)
    mermaid = render_mermaid(models, relationships)

    SCHEMA_DOC.write_text(
        render_schema_doc(models, unmanaged_models, relationships),
        encoding="utf-8",
    )
    ER_MERMAID.write_text(mermaid, encoding="utf-8")
    ER_DOC.write_text(render_er_doc(mermaid, models, relationships), encoding="utf-8")

    print(f"Wrote {SCHEMA_DOC.relative_to(ROOT_DIR)}")
    print(f"Wrote {ER_DOC.relative_to(ROOT_DIR)}")
    print(f"Wrote {ER_MERMAID.relative_to(ROOT_DIR)}")
    print(f"Managed tables: {len(models)}")
    print(f"Relationships: {len(relationships)}")


if __name__ == "__main__":
    main()

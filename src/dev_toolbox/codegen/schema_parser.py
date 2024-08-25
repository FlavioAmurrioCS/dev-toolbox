from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from typing import Literal, TypedDict, Union
    from typing_extensions import TypeIs
    from typing_extensions import NotRequired

    RefDraft = TypedDict("RefDraft", {"$ref": str})

    class EnumDraft(TypedDict):
        enum: list[str]

    class ArrayDraft(TypedDict):
        type: Literal["array"]
        items: NotRequired[JsonSchema]

    class ObjectDraft(TypedDict):
        type: Literal["object"]
        properties: dict[str, JsonSchema]
        required: NotRequired[list[str]]

    class PrimitiveDraft(TypedDict):
        type: Literal["string", "number", "integer", "boolean"]

    class AnyOfDraft(TypedDict):
        anyOf: list[ArrayDraft | ObjectDraft | PrimitiveDraft]

    class UnionDraft(TypedDict):
        type: list[str]

    JsonSchema = Union[
        ArrayDraft,
        ObjectDraft,
        PrimitiveDraft,
        AnyOfDraft,
        RefDraft,
        EnumDraft,
        UnionDraft,
    ]


PRIMITIVE_TYPE_CONVERSION = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "number": "float",
    "null": "None",
}

###############################################################################
# region: TypeGuards
###############################################################################


def union_draft_is(value: JsonSchema) -> TypeIs[UnionDraft]:
    return isinstance(value.get("type"), list)


def object_draft_is(value: JsonSchema) -> TypeIs[ObjectDraft]:
    return value.get("type") == "object"


def array_draft_is(value: JsonSchema) -> TypeIs[ArrayDraft]:
    return value.get("type") == "array"


def anyof_draft_is(value: JsonSchema) -> TypeIs[AnyOfDraft]:
    return "anyOf" in value


def primitive_draft_is(value: JsonSchema) -> TypeIs[PrimitiveDraft]:
    return value.get("type") in ["string", "number", "integer", "boolean", "null"]


def ref_draft_is(value: JsonSchema) -> TypeIs[RefDraft]:
    return "$ref" in value


def enum_draft_is(value: JsonSchema) -> TypeIs[EnumDraft]:
    return "enum" in value


###############################################################################
# endregion: TypeGuards
###############################################################################


def object_draft_parse(
    *, draft: ObjectDraft, property_name: str, lines: list[tuple[str, ...]]
) -> str:
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    has_proper_properties_names = all(pattern.match(name) for name in draft["properties"])
    clazz_name = property_name.capitalize()

    start = f"class {clazz_name}(TypedDict):"
    end = ""
    joiner = ""
    qoutes = ""
    if not has_proper_properties_names:
        start = f'{clazz_name} = TypedDict("{clazz_name}", {{'
        joiner = ","
        end = "})"
        qoutes = '"'
    buffer = [start]
    required = set(draft.get("required", []))
    for name, ztype in draft["properties"].items():
        type_s = _parse_draft(draft=ztype, property_name=name, lines=lines)
        if name not in required:
            type_s = f"NotRequired[{type_s}]"
        buffer.append(f"    {qoutes}{name}{qoutes}: {type_s}{joiner}")

    buffer.append(end)
    lines.append(tuple(buffer))

    return clazz_name


def _parse_draft(*, draft: JsonSchema, property_name: str, lines: list[tuple[str, ...]]) -> str:  # noqa: PLR0911
    if not draft:
        return "Any"
    if enum_draft_is(draft):
        type_s = ",\n    ".join([f'"{x}"' for x in draft["enum"]])
        clazz_name = property_name.capitalize()
        lines.append((f"{clazz_name} = Literal[\n    {type_s},\n]",))
        return clazz_name
    if ref_draft_is(draft):
        return draft["$ref"].rsplit("/", maxsplit=1)[-1]
    if object_draft_is(draft):
        return object_draft_parse(draft=draft, property_name=property_name, lines=lines)
    if array_draft_is(draft):
        dp: JsonSchema = draft.get("items", {})  # type: ignore
        parsed_type = _parse_draft(draft=dp, property_name=property_name, lines=lines)
        return f"List[{parsed_type}]"
    if anyof_draft_is(draft):
        types_str = ", ".join(
            _parse_draft(draft=d, property_name=property_name, lines=lines) for d in draft["anyOf"]
        )
        types_str = f"Union[{types_str}]"
        if draft.get("title") is None:
            return types_str
        clazz_name: str = draft["title"]  # type: ignore
        lines.append((f"{clazz_name} = {types_str}",))
        return f"{clazz_name}"
    if primitive_draft_is(draft):
        return PRIMITIVE_TYPE_CONVERSION[draft["type"]]
    if union_draft_is(draft):
        types_str = ", ".join(PRIMITIVE_TYPE_CONVERSION[x] for x in draft["type"])
        return f"Union[{types_str}]"
    msg = f"Unknown draft type {draft=}"
    logging.error(msg)
    return "Any"


def schema_to_types(schema: JsonSchema) -> str:
    lines: list[tuple[str, ...]] = [
        (
            "from typing import TypedDict, Union, Literal, List",
            "from typing_extensions import NotRequired",
            "",
        )
    ]
    definitions: dict[str, JsonSchema] = schema.get("definitions", {})  # type: ignore[assignment]
    for key, value in reversed(definitions.items()):
        _parse_draft(draft=value, property_name=key, lines=lines)
    last_type = _parse_draft(draft=schema, property_name="root", lines=lines)
    buffer = "\n\n".join("\n".join(line) for line in lines)
    if "]" in last_type:
        return buffer + f"\n\nRoot = {last_type}"
    return buffer


def main(argv: Sequence[str] | None = None) -> int:
    import json
    import argparse
    from textwrap import dedent

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter,
        add_help=True,
        description="Converts a JSON schema to TypedDicts.",
        epilog=dedent("""\
            Examples:

                # Convert a JSON schema to TypedDicts.
                $ %(prog)s --input=schema.json --output=schema.py

                # Convert sample JSON data to TypedDicts using quicktype, a NPM package.
                $ quicktype --lang=schema data.json | %(prog)s --output=schema.py

                # Convert sample JSON data to TypedDicts using genson, a Python package.
                $ genson data.json | %(prog)s --output=schema.py

                # Convert sample JSON data to TypedDicts with datamodel-codegen, a Python package.
                $ datamodel-codegen --output-model-type=typing.TypedDict --input=data.json
            """),
    )
    parser.add_argument(
        "--input",
        type=str,
        help="The input JSON schema file.",
        default="/dev/stdin",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="The output Python file.",
        default="/dev/stdout",
    )
    args = parser.parse_args(argv)

    with open(args.input) as f, open(args.output, "w") as out:
        schema: JsonSchema = json.load(f)
        out.write(schema_to_types(schema) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            [
                "--input=/Users/flavio/dev/github.com/FlavioAmurrioCS/dev-toolbox/tests/codegen_resources/book_schema.json"
            ]
        )
    )

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
        additionalProperties: NotRequired[JsonSchema]

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


def to_pascal_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return "".join(x.title() for x in components)


def object_draft_parse(
    *, draft: ObjectDraft, property_name: str, lines: dict[tuple[str, ...], None]
) -> str:
    property_name = str(draft.get("title", property_name))
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    properties = draft.get("properties", {})
    if not properties:
        # Note: Not sure if this is the best way to handle this case.
        type_s = _parse_draft(
            draft=draft.get("additionalProperties", {}),  # type: ignore[arg-type]
            property_name=property_name,
            lines=lines,
        )
        return f"Dict[str, {type_s}]"
    has_proper_properties_names = all(pattern.match(name) for name in properties)
    clazz_name = property_name
    if clazz_name[0].upper() != clazz_name[0]:
        # clazz_name = clazz_name.capitalize()  # Rethink capitalization to be CamelCase
        clazz_name = to_pascal_case(clazz_name)  # Rethink capitalization to be CamelCase
    if clazz_name.isnumeric():
        clazz_name = f"_{clazz_name}"

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
    for name, ztype in properties.items():
        type_s = _parse_draft(draft=ztype, property_name=name, lines=lines)
        if name not in required:
            type_s = f"NotRequired[{type_s}]"
        buffer.append(f"    {qoutes}{name}{qoutes}: {type_s}{joiner}")

    buffer.append(end)
    lines[tuple(buffer)] = None

    return clazz_name


def _parse_draft(  # noqa: PLR0911
    *, draft: JsonSchema, property_name: str, lines: dict[tuple[str, ...], None]
) -> str:
    if not draft:
        return "Any"
    if enum_draft_is(draft):
        type_s = ",\n    ".join([f'"{x}"' for x in draft["enum"]])
        clazz_name = property_name.capitalize()
        lines[(f"{clazz_name} = Literal[\n    {type_s},\n]",)] = None
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
        lines[(f"{clazz_name} = {types_str}",)] = None
        return f"{clazz_name}"
    if primitive_draft_is(draft):
        return PRIMITIVE_TYPE_CONVERSION[draft["type"]]
    if union_draft_is(draft):
        types_str = ", ".join(PRIMITIVE_TYPE_CONVERSION[x] for x in draft["type"])
        return f"Union[{types_str}]"
    msg = f"Unknown draft type {draft=}"
    logging.error(msg)  # noqa: LOG015
    return "Any"


def schema_to_types(schema: JsonSchema) -> str:
    lines: dict[tuple[str, ...], None] = {
        (
            "from typing import TypedDict, Union, Literal, List, Dict",
            "from typing_extensions import NotRequired",
            "",
        ): None
    }
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


# def _test() -> None:
#     from dev_toolbox.http.great_value import gv_request
#     from dev_toolbox.multi_file import MultiFileOpener
#     import os
#     import subprocess
#     import json
#     from textwrap import dedent

#     python_code = dedent("""\
#         from genson import SchemaBuilder
#         import json
#         import sys
#         builder = SchemaBuilder()
#         file = sys.argv[1]
#         with open(file) as f:
#             builder.add_object(json.load(f))
#         print(builder.to_json(indent=2))
#         """)

#     files = (
#         "getting-started.json",
#         "bitcoin-block.json",
#         "null-safe.json",
#         "pokedex.json",
#         "simple-object.json",
#         "spotify-album.json",
#         "us-senators.json",
#         "kitchen-sink.json",
#         "reddit.json",
#         "us-avg-temperatures.json",
#         "github-events.json",  # Report genson issue
#     )
#     with MultiFileOpener(  # type: ignore[var-annotated]
#         filenames=("genson", "quicktype"),
#         base_dir="/tmp",
#         extension=".py",
#     ) as mfo:
#         for file in files:
#             filepath = "/tmp/" + file
#             print(file)
#             if not os.path.exists(filepath):
#                 response = gv_request.request(
#                     method="GET",
#                     url=f"https://raw.githubusercontent.com/glideapps/quicktype/master/test/inputs/json/samples/{file}",
#                 )
#                 with open(filepath, "wb") as f:
#                     f.write(response.response.read())

#             mfo["genson"].write("#" * 100 + "\n# region: " + file + "\n" + "#" * 100 + "\n\n")
#             try:
#                 result = subprocess.run(
#                     [
#                         "/Users/flavio/opt/runtool/pipx_home/venvs/genson/bin/python",
#                         "-c",
#                         python_code,
#                         filepath,
#                     ],
#                     # ["/Users/flavio/opt/runtool/bin/genson", filepath],
#                     check=True,
#                     capture_output=True,
#                 )
#                 schema = json.loads(result.stdout)
#                 mfo["genson"].write(schema_to_types(schema) + "\n")
#             except Exception as e:
#                 mfo["genson"].write(f"# Error: {e}\n")
#                 raise
#             mfo["genson"].write("#" * 100 + "\n# endregion: " + file + "\n" + "#" * 100 + "\n\n")

#             mfo["quicktype"].write("#" * 100 + "\n# region: " + file + "\n" + "#" * 100 + "\n\n")
#             try:
#                 result = subprocess.run(
#                     ["/Users/flavio/.node_global/bin/quicktype", "--lang=schema", filepath],
#                     check=True,
#                     capture_output=True,
#                 )
#                 schema = json.loads(result.stdout)
#                 mfo["quicktype"].write(schema_to_types(schema) + "\n")
#             except Exception as e:
#                 mfo["quicktype"].write(f"# Error: {e}\n")
#                 raise
#             mfo["quicktype"].write("#" * 100 + "\n# endregion: " + file + "\n" + "#" * 100 + "\n\n")  # noqa: E501


if __name__ == "__main__":
    raise SystemExit(main())

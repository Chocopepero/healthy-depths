from google.genai import types

check_drug_interactions_decl = types.FunctionDeclaration(
    name="check_drug_interactions",
    description="Check for known drug interactions and adverse events via OpenFDA for a list of medications the patient is currently taking.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "medications": types.Schema(
                type="ARRAY",
                items=types.Schema(type="STRING"),
                description="List of medication names to check",
            )
        },
        required=["medications"],
    ),
)

DEPTH_TOOLS = types.Tool(
    function_declarations=[check_drug_interactions_decl]
)

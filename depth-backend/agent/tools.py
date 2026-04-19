import google.generativeai as genai

search_knowledge_base_decl = genai.protos.FunctionDeclaration(
    name="search_knowledge_base",
    description="Search the medical knowledge base (MedlinePlus, CDC, OpenFDA docs) for information about symptoms, conditions, or medications.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "query": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The search query — a symptom, condition, or medication name",
            )
        },
        required=["query"],
    ),
)

check_drug_interactions_decl = genai.protos.FunctionDeclaration(
    name="check_drug_interactions",
    description="Check for known drug interactions and adverse events via OpenFDA for a list of medications the patient is currently taking.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "medications": genai.protos.Schema(
                type=genai.protos.Type.ARRAY,
                items=genai.protos.Schema(type=genai.protos.Type.STRING),
                description="List of medication names to check",
            )
        },
        required=["medications"],
    ),
)

find_clinics_decl = genai.protos.FunctionDeclaration(
    name="find_clinics",
    description="Find nearby free or low-cost federally qualified health centers (FQHCs) using the patient's ZIP code.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "zip_code": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Patient's ZIP code",
            ),
            "radius": genai.protos.Schema(
                type=genai.protos.Type.INTEGER,
                description="Search radius in miles (default 10)",
            ),
        },
        required=["zip_code"],
    ),
)

DEPTH_TOOLS = genai.protos.Tool(
    function_declarations=[
        search_knowledge_base_decl,
        check_drug_interactions_decl,
        find_clinics_decl,
    ]
)

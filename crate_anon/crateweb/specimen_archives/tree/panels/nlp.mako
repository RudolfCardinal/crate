## -*- coding: utf-8 -*-
## crate_anon/crateweb/specimen_archives/tree/panels/nlp.mako
<%inherit file="../base.mako"/>
<%!

from typing import List
from crate_anon.crateweb.core.utils import (
    JavascriptBranchNode,
    JavascriptLeafNode,
    JavascriptTree,
    url_with_querystring,
)
from crate_anon.crateweb.research.archive_func import template_html


COMMON_END_COLUMNS = [
    "_content", "relation", "tense",
]
SIMPLE_NUMERIC_COLUMNS = [
    "value_text", "units",
] + COMMON_END_COLUMNS
NUMERATOR_DENOMINATOR_COLUMNS = [
    "numerator", "denominator",
] + COMMON_END_COLUMNS


%>

<%namespace name="subtree" file="../snippets/subtree.mako"/>

<%

def nlp_url(tablename: str, description: str, columns: List[str]) -> str:
    qparams = {
        "tablename": tablename,
        "description": description,
        "column_csv": ",".join(columns),
    }
    return template_html(
        archive_url("snippets/single_nlp_page.mako"),
        **qparams
    )


tree = JavascriptTree(
    tree_id="nlp_tree",
    child_id_prefix="nlp_tree_child_",
    children=[
        JavascriptBranchNode("Biochemistry", [
            JavascriptLeafNode("Na", nlp_url(
                "sodium", "Sodium (Na)",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("K", nlp_url(
                "potassium", "Potassium (K)",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Urea", nlp_url(
                "urea", "Urea",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Creatinine", nlp_url(
                "creatinine", "Creatinine",
                ["value_micromol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Glucose", nlp_url(
                "glucose", "Glucose",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),

            JavascriptLeafNode("CRP", nlp_url(
                "crp", "C-reactive protein",
                ["value_mg_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("TSH", nlp_url(
                "tsh", "Thyroid-stimulating hormone (TSH)",
                ["value_mU_L"] + SIMPLE_NUMERIC_COLUMNS
            )),

            JavascriptLeafNode("HbA1c", nlp_url(
                "hba1c", "Glycosylated haemoglobin (HbA1c)",
                ["value_mmol_mol"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Total cholesterol", nlp_url(
                "totalcholesterol", "Total cholesterol",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("HDL cholesterol", nlp_url(
                "hdlcholesterol", "High-density lipoprotein (HDL) cholesterol",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("LDL cholesterol", nlp_url(
                "ldlcholesterol", "Low-density lipoprotein (LDL) cholesterol",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Triglycerides", nlp_url(
                "triglycerides", "Triglycerides (TG)",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),

            JavascriptLeafNode("Lithium", nlp_url(
                "lithium", "Lithium (Li)",
                ["value_mmol_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
        ]),
        JavascriptBranchNode("Clinical", [
            JavascriptLeafNode("BP", nlp_url(
                "bp", "Blood pressure (BP)",
                ["systolic_bp_mmhg",
                 "diastolic_bp_mmhg"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Height", nlp_url(
                "height", "Height",
                ["value_m"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Weight", nlp_url(
                "weight", "Weight",
                ["value_kg"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("BMI", nlp_url(
                "bmi", "Body mass index (BMI)",
                ["value_kg_per_sq_m"] + SIMPLE_NUMERIC_COLUMNS
            )),
        ]),
        JavascriptBranchNode("Cognitive", [
            JavascriptLeafNode("ACE", nlp_url(
                "ace", "Addenbrooke’s Cognitive Examination (ACE-R, ACE-III)",
                ["out_of_100"] + NUMERATOR_DENOMINATOR_COLUMNS
            )),
            JavascriptLeafNode("Mini-ACE", nlp_url(
                "miniace", "Mini-Addenbrooke’s Cognitive Examination (Mini-ACE)",
                ["out_of_30"] + NUMERATOR_DENOMINATOR_COLUMNS
            )),
            JavascriptLeafNode("MMSE", nlp_url(
                "mmse", "Mini-Mental State Examination (MMSE)",
                ["out_of_30"] + NUMERATOR_DENOMINATOR_COLUMNS
            )),
            JavascriptLeafNode("MOCA", nlp_url(
                "moca", "Montreal Cognitive Assessment (MOCA)",
                ["out_of_30"] + NUMERATOR_DENOMINATOR_COLUMNS
            )),
        ]),
        JavascriptBranchNode("Haematology", [
            JavascriptLeafNode("White blood cells", nlp_url(
                "wbc", "White blood cell (WBC, leukocyte) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Haemoglobin", nlp_url(
                "haemoglobin", "Haemoglobin (Hb)",
                ["value_g_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Haematocrit", nlp_url(
                "haematocrit", "Haematocrit (Hct)",
                ["value_L_L"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Red blood cells", nlp_url(
                "rbc", "Red blood cell (RBC) count",
                ["value_trillion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Platelets", nlp_url(
                "platelets", "Platelet (Plt) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),

            JavascriptLeafNode("Neutrophils", nlp_url(
                "neutrophils", "Neutrophil (LØ) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Lymphocytes", nlp_url(
                "lymphocytes", "Lymphocyte (LØ) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Monocytes", nlp_url(
                "monocytes", "Monocyte (MØ) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Basophils", nlp_url(
                "basophils", "Basophil (BØ) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),
            JavascriptLeafNode("Eosinophils", nlp_url(
                "eosinophils", "Eosinophil (EØ) count",
                ["value_billion_per_l"] + SIMPLE_NUMERIC_COLUMNS
            )),

            JavascriptLeafNode("ESR", nlp_url(
                "esr", "Erythrocyte sedimentation rate (ESR)",
                ["value_mm_h"] + SIMPLE_NUMERIC_COLUMNS
            )),
        ]),
        JavascriptBranchNode("Pharmacy", [
            JavascriptLeafNode("KCL/GATE drugs", nlp_url(
                "medications_gate", "Drugs (via KCL/GATE pharmacotherapy app)",
                [
                    "drug", "drug_type",
                    "dose", "dose_value", "dose_unit", "dose_multiple",
                    "route", "status", "tense",
                    "experiencer",
                    "frequency", "interval", "unit_of_time",
                ]
            )),
            JavascriptLeafNode("MedEx drugs", nlp_url(
                "medications_medex", "Drugs (via MedEx)",
                [
                    "drug", "generic_name", "brand",
                    "form", "strength", "dose_amount", "route",
                    "frequency", "duration", "necessity",
                    "sentence_text",
                ]
            )),
        ]),
        JavascriptBranchNode("Pathology", [
            JavascriptLeafNode("KConnect diseases", nlp_url(
                "kconnect_diseases", "Diseases (via KConnect/BioYODIE app)",
                [
                    "pref",
                    "negation",
                    "experiencer",
                    "temporality",
                    "inst",
                ]
            )),
            JavascriptLeafNode("KCL Lewy body dementia", nlp_url(
                "lewy_body_dementia_gate", "Lewy body dementia (LBD, DBL) (via KCL GATE app)",
                [
                    "rule", "text",
                ]
            )),
        ]),
    ]
)
# log.critical(repr(tree))

%>

${subtree.subtree_page(tree=tree, page_title="Natural language processing", no_content_selected="Choose a NLP processor.")}


#!/usr/bin/env python

"""
Autogenerated NLP processor definition file, to be imported by the CRATE
NLPRP web server. The PROCESSORS variable is the one of interest.
"""

# =============================================================================
# Imports
# =============================================================================

from crate_anon.nlp_manager.all_processors import (
    all_crate_python_processors_nlprp_processor_info
)
from crate_anon.nlprp.constants import NlprpKeys as NKeys
from crate_anon.nlp_webserver.constants import (
    KEY_PROCTYPE,
    PROCTYPE_GATE,
)


# =============================================================================
# Processor definitions
# =============================================================================

# GATE processors correct as of 19/04/2019 for KCL server.
# Python processors are automatic, as below.

PROCESSORS = [
    # -------------------------------------------------------------------------
    # GATE processors
    # -------------------------------------------------------------------------
    {
        NKeys.NAME: "medication",
        NKeys.TITLE: "GATE processor: Medication tagger",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of drug prescriptions, "
                           "including the dose, route and frequency.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "diagnosis",
        NKeys.TITLE: "GATE processor: Diagnosis finder",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of diagnoses, in words or "
                           "in coded form.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "blood-pressure",
        NKeys.TITLE: "GATE processor: Blood Pressure",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of blood pressure measurements.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "cbt",
        NKeys.TITLE: "GATE processor: Cognitive Behavioural Therapy",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies mentions of cases where the patient "
                           "has attended CBT sessions.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "lives-alone",
        NKeys.TITLE: "GATE processor: Lives Alone",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies if the patient lives alone.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "mmse",
        NKeys.TITLE: "GATE processor: Mini-Mental State Exam Result Extractor",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "The Mini-Mental State Exam (MMSE) Results "
                           "Extractor finds the results of this common "
                           "dementia screening test within documents along "
                           "with the date on which the test was administered.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "bmi",
        NKeys.TITLE: "GATE processor: Body Mass Index",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of BMI scores.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "smoking",
        NKeys.TITLE: "GATE processor: Smoking Status Annotator",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies instances of smoking being discussed "
                           "and determines the status and subject (patient or "
                           "someone else).",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "ADR",
        NKeys.TITLE: "GATE processor: ADR",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Adverse drug event mentions in clinical notes.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "suicide",
        NKeys.TITLE: "GATE processor: Symptom finder - Suicide",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "App derived from TextHunter project suicide.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "appetite",
        NKeys.TITLE: "GATE processor: Symptom finder - Appetite",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds markers of good or poor appetite.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
    {
        NKeys.NAME: "low_mood",
        NKeys.TITLE: "GATE processor: Symptom finder - Low_Mood",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "App derived from TextHunter project low_mood.",
        KEY_PROCTYPE: PROCTYPE_GATE
    },
] + all_crate_python_processors_nlprp_processor_info()


# =============================================================================
# Convenience method: if you run the file, it prints its results.
# =============================================================================

if __name__ == "__main__":
    import json  # delayed import
    print(json.dumps(PROCESSORS, indent=4, sort_keys=True))



# Generated at 2019-08-12 00:05:01
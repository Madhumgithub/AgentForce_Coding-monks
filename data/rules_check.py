# rules_check.py
import re, json

CHECKS = [
  {"id":"payment_terms_missing","desc":"Payment terms missing", "pattern": r"(payment|invoice|due within|net\s*\d{1,2})", "positive": True},
  {"id":"liability_missing","desc":"Liability / limitation missing", "pattern": r"(liability|limitation of liability|liable for)", "positive": True},
  {"id":"auto_renewal","desc":"Contains auto-renewal", "pattern": r"(auto-?renew|automatically renew|renewal will be)", "positive": True},
  {"id":"termination_missing","desc":"Termination clause missing", "pattern": r"(terminate|termination|terminate for convenience)", "positive": True},
  {"id":"confidentiality_missing","desc":"Confidentiality / NDA missing", "pattern": r"(confidential|non[- ]disclosure|nda|confidential information)", "positive": True},
  {"id":"penalty_clause","desc":"Penalty or late fee mentioned", "pattern": r"(late fee|penalt|interest at .*%|liquidated damages)", "positive": True}
]

def run_checks(text):
    text_l = text.lower()
    flags = []
    for c in CHECKS:
        found = bool(re.search(c["pattern"], text_l))
        if not found:
            # if clause expected but not found -> flag
            flags.append({"id":c["id"], "desc":c["desc"], "present":False})
        else:
            flags.append({"id":c["id"], "desc":c["desc"], "present":True})
    return flags

if __name__=="__main__":
    txt = open("parsed.txt","r",encoding="utf8").read()
    flags = run_checks(txt)
    print(json.dumps(flags, indent=2))
    json.dump(flags, open("flags.json","w"), indent=2)

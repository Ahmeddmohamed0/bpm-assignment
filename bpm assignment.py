
import csv
from itertools import combinations

# =====================================================================
# QUESTION 1: data quality on Q1_raw_event_log.csv
# =====================================================================
OFFICIAL = ["Post Job", "Screen Resumes", "Phone Interview", "Technical Test",
            "Onsite Interview", "Reference Check", "Extend Offer", "Onboard Candidate"]
MANDATORY = "onsite interview"         

rows = []
with open("Q1_raw_event_log.csv", newline="") as f:

    reader = csv.reader(f)

    next(reader)

    for r in reader:
        
        rows.append(r)

print("== QUESTION 1 ==")
print("Q1.1  rows:", len(rows))

case_ids = set()
for r in rows:
    if r[0] != "":
        case_ids.add(r[0])
print("Q1.2  distinct case ids:", len(case_ids))

empty_case = 0
empty_ts = 0
date_only = 0
empty_res = 0
for r in rows:

    if r[0] == "":

        empty_case += 1
    if r[2] == "":

        empty_ts += 1
    elif len(r[2]) == 10:  

        date_only += 1
    if r[3] == "":
        empty_res += 1
print("Q1.3  empty case id:", empty_case)
print("Q1.4  empty timestamp:", empty_ts)
print("Q1.5  date without time:", date_only)
print("Q1.6  empty resource:", empty_res)

# Q1.7
seen = set()
duplicates = 0

for r in rows:

    key = tuple(r)
    if key in seen:

        duplicates += 1
    else:

        seen.add(key)
print("Q1.7  duplicate rows:", duplicates)

# Q1.8 and Q1.9

activity_strings = set()

not_official = 0
for r in rows:

    activity_strings.add(r[1])

    if r[1] not in OFFICIAL:
        not_official += 1
print("Q1.8  distinct activity strings:", len(activity_strings))
print("Q1.9  not official activity:", not_official)

# Q1.10
cases_with_mandatory = set()
for r in rows:

    label = r[1].strip().lower().replace("_", " ")

    if r[0] != "" and label == MANDATORY:

        cases_with_mandatory.add(r[0])

print("Q1.10 cases without Onsite Interview:", len(case_ids) - len(cases_with_mandatory))

# Q1.11
last_ts = {}
bad_cases = set()
for r in rows:
    case, ts = r[0], r[2]

    if case == "" or len(ts) != 19:

        continue
    if case in last_ts and ts < last_ts[case]:

        bad_cases.add(case)

        print("out of order:", case, ts, "after", last_ts[case])

    last_ts[case] = ts
    
print("Q1.11 cases out of order:", len(bad_cases))
# Q1.12
total_per_activity = {}
empty_per_activity = {}
for r in rows:

    label = r[1].strip().lower().replace("_", " ")

    total_per_activity[label] = total_per_activity.get(label, 0) + 1

    if r[3] == "":

        empty_per_activity[label] = empty_per_activity.get(label, 0) + 1

print("Q1.12 empty resource per activity (empty / total):")
for label in empty_per_activity:

    print("    ", label, empty_per_activity[label], "/", total_per_activity[label])

print("       if ALL rows of one activity are empty -> CONT (answer 1)")

# Q1.13
counts = {1: empty_ts, 2: date_only, 3: empty_res, 4: duplicates,
          5: not_official, 6: empty_case,
          7: len(case_ids) - len(cases_with_mandatory), 8: len(bad_cases)}
print("Q1.13 counts:", counts)
print("       largest issue number:", max(counts, key=counts.get))

# =====================================================================
# QUESTION 2: footprint matrix and alpha algorithm on Q2_clean_event_log.csv
# =====================================================================
letters = {"Extend Offer": "a", "Onboard Candidate": "b", "Onsite Interview": "c",
           "Phone Interview": "d", "Post Job": "e", "Reference Check": "f",
           "Screen Resumes": "g", "Technical Test": "h"}
ACT = "abcdefgh"


trace_of_case = {}
with open("Q2_clean_event_log.csv", newline="") as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        case = r[0]
        if case not in trace_of_case:
            trace_of_case[case] = ""
        trace_of_case[case] += letters[r[1]]

traces = set(trace_of_case.values())   

print()
print("===== QUESTION 2 =====")
print("Q2.1  distinct traces:", len(traces))

# follow relation
follows = set()
for t in traces:
    for i in range(len(t) - 1):
        follows.add((t[i], t[i + 1]))
print("Q2.2  pairs x >L y:", len(follows))

def relation(x, y):
    xy = (x, y) in follows
    yx = (y, x) in follows
    if xy and not yx:
        return "->"
    if yx and not xy:
        return "<-"
    if xy and yx:
        return "||"
    return "#"

causal = 0
parallel = 0
choice = 0
print("Q2.14 footprint matrix (upper half):")

for x, y in combinations(ACT, 2):        
    rel = relation(x, y)
    print("       ", x, y, rel)
    if rel == "->" or rel == "<-":
        causal += 1
    elif rel == "||":
        parallel += 1
    else:
        choice += 1
print("Q2.3  causality pairs:", causal)
print("Q2.4  parallel pairs:", parallel)
print("Q2.5  # pairs:", choice)
TI = sorted(set(t[0] for t in traces))
TO = sorted(set(t[-1] for t in traces))
print("Q2.6  |TI|:", len(TI))
print("Q2.7  TI:", ",".join(TI))
print("Q2.8  |TO|:", len(TO))
print("Q2.9  TO:", ",".join(TO))
#step 4:
def all_sharp(group):

    for x in group:

        for y in group:

            if x == y:

                if (x, x) in follows:     # x # X
                    return False
            elif relation(x, y) != "#":

                return False
    return True

groups = []

for size in range(1, len(ACT) + 1):

    for g in combinations(ACT, size):

        if all_sharp(g):
            groups.append(g)

XL = []
for A in groups:
    for B in groups:
        ok = True
        for x in A:
            for y in B:
                if relation(x, y) != "->":    
                    ok = False
        if ok:
            XL.append((A, B))
print("Q2.10 |XL|:", len(XL))

# step 5:

YL = []

for (A, B) in XL:
    maximal = True
    for (C, D) in XL:

        if (A, B) != (C, D) and set(A) <= set(C) and set(B) <= set(D):
            maximal = False
    if maximal:

        YL.append((A, B))
print("Q2.11 |YL|:", len(YL))
for pair in YL:
    print("     ", pair)

# step 6 and 7
print("Q2.12 places:", len(YL) + 2)      
arcs = len(TI) + len(TO)                 
for (A, B) in YL:
    arcs += len(A) + len(B)               
print("Q2.13 arcs:", arcs)

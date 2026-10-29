"""Source-reviewed specialty guide; deliberately conservative matching to admissions catalog.

The descriptions are *program examples*, not universal career promises, curricula or admissions rules.
"""
import json
from pathlib import Path
from functools import lru_cache
import catalog

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT/'data'/'specialties.json').read_text(encoding='utf-8'))
PROFILES = DATA['profiles']
BY_ID = {p['id']:p for p in PROFILES}
assert len(BY_ID) == len(PROFILES)

@lru_cache(maxsize=1)
def aliases():
    output={}
    for p in PROFILES:
        for alias in p['aliases']:
            key=catalog.norm(alias)
            if not key or (key in output and output[key]!=p['id']):
                raise ValueError('Specialty alias conflict: '+alias)
            output[key]=p['id']
    return output

def identify(program, university=''):
    """Match full slash-delimited names only; no fuzzy/partial guessing.

    Programs containing multiple distinct specialty labels are intentionally not matched.
    Do not map institute technical diplomas to bachelor-level specialty cards.
    """
    name=catalog.display(program)
    if 'معهد' in name or 'معهد' in university:
        return None
    ids=set()
    for segment in name.split('/'):
        key=catalog.norm(segment)
        if key in aliases():ids.add(aliases()[key])
    return next(iter(ids)) if len(ids)==1 else None

def list_profiles(q='',category=''):
    if len(q)>120:raise ValueError('query too long')
    key=catalog.norm(q)
    return [{k:v for k,v in p.items() if k!='aliases'} for p in PROFILES if (not category or p['category']==category) and (not key or key in catalog.norm(p['title']+' '+p['overview']+' '+' '.join(p['subjects'])))]

from typing import List, Tuple
from sympy import Symbol

from .evaluate import parse_annotation
from .evaluatep import cmp_question

## ===== Sentence Counter =====

def cnt_sentences(annotation, include_dec = True):
    """
    Count the number of sentences in an annotation.
    """
    (vars, facts, queries), _, _ = parse_annotation(annotation)
    cnt = len(facts) + len(queries)
    if include_dec:
        cnt += len(vars)
    return cnt

## ===== Algorithm for diff ======

def align2diff(
        best_alignments: List[List[Tuple[int, int]]], 
        filtered: Tuple[List[str], List[str]]
    ) -> str:
    """
    Generate a diff log for two annotations, based on the return value
    from `cmp_question`. Return a human-readable diff string.

    Only pick the first element in `best_alignment`.
    """
    assert len(best_alignments) > 0, "Empty alignment in diff!"

    filtered1, filtered2 = filtered
    idx1, idx2 = map(lambda x: list(range(len(x))), filtered)

    alignment = best_alignments[0]
    for align1, align2 in alignment:
        if align1 in idx1: idx1.remove(align1)
        if align2 in idx2: idx2.remove(align2)

    diff_string = ""
    if idx1 and idx2:
        diff_string += '\n'.join(f"< {s}" for s in map(lambda x: filtered1[x], idx1))
        diff_string += '\n---\n'
        diff_string += '\n'.join(f"> {s}" for s in map(lambda x: filtered2[x], idx2))
    elif idx1:
        diff_string += '\n'.join(f"< {s}" for s in map(lambda x: filtered1[x], idx1))
    elif idx2:
        diff_string += '\n'.join(f"> {s}" for s in map(lambda x: filtered2[x], idx2))

    return diff_string

def diff(
        annotation1: str, 
        annotation2: str, 
        include_dec: bool = True,
        verbose: bool = False, 
        max_workers: int = None,
        speed_up: bool = True
    ) -> str:
    """
    Generate a diff log for two annotations. Return a human-readable diff string.
    """
    _, aligns, filtered = cmp_question(annotation1, annotation2, include_dec, verbose, max_workers, speed_up)
    diff_log: str = align2diff(aligns, filtered)
    return diff_log


## ===== Filter annotations =====

def filter_annotation(annotation: str) -> str:
    """
    Filter out invalid sentences in an annotation. Usually embedded
    after the model predictions.
    """
    ## remove invalid sentences
    (vars, facts, queries), to_filter, alignment = parse_annotation(annotation)

    ## check used variables
    used_vars = set()
    for expr in facts + queries:
        used_vars = used_vars.union(expr.free_symbols)
    unused_vars = set(vars).difference(used_vars)
    undeclared_vars = used_vars.difference(set(vars).union({Symbol('x'), Symbol('y')}))

    declared_and_used_vars = set(vars).intersection(used_vars)
    filtered = [f"{v}: {v.type}" for v in declared_and_used_vars]

    ## remove same facts
    for idx in alignment['facts'].values():
        filtered.append(to_filter[idx])

    for expr in queries:
        idx = alignment['queries'][expr]
        filtered.append(to_filter[idx])

    return '\n'.join(filtered) if filtered else ''
    
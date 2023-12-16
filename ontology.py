# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:53:38 2023

@author: dwgre
"""
import hashlib

WORDHASH = {}
HASHWORD = {}
ALLWORDS = {}
HASHCATEGORY = {}
CATEGORYHASH = {}



def myHash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def build_ontology(filename):
    global WORDHASH, ALLWORDS, HASHWORD, HASHCATEGORY, CATEGORYHASH

    WORDHASH = {}
    HASHWORD = {}
    HASHCATEGORY = {}
    CATEGORYHASH = {}
    ALLWORDS = {}
    with open(filename, encoding="utf-8") as fp:
        text_blob = fp.read()
    for line in text_blob.split("\n"):
        if not line.strip():
            continue
        x = line.split(">")
        tags = x[0]
        categories = []
        if len(x) > 1:
            categories = x[1].split(",")
        tags = tags.split(",")
        hashVal = hash("-".join(tags))
        for _t in tags:
            WORDHASH[_t] = hashVal
            ALLWORDS[myHash(_t)] = _t
        HASHWORD[hashVal] = tags
        HASHCATEGORY[hashVal] = categories
        for catg in categories:
            if catg not in CATEGORYHASH:
                CATEGORYHASH[catg] = []
            CATEGORYHASH[catg] = list(set(CATEGORYHASH[catg] + [hashVal]))

def get_hash(word):
    if word in WORDHASH:
        return WORDHASH[word]
    hashVal = hash(word)
    WORDHASH[word] = hashVal
    return hashVal

def getTags(word):
    global WORDHASH
    global HASHWORD
    global HASHCATEGORY
    out = []
    if word not in WORDHASH:
        return out
    hashVal = WORDHASH[word]
    out = list(set(HASHWORD[hashVal] + [word]))
    for catg in HASHCATEGORY[hashVal]:
        out = out + getTags(catg)
        #print(f"{word} -> {out}")
    return out

def reload():
    build_ontology("ontology.txt")
    
reload()
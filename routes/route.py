from fastapi import APIRouter, File, UploadFile
from models.candidates import Candidate
from config.database import collection_name 
from schema.schemas import list_serializer, individual_serializer
from bson import ObjectId
from pdfminer.high_level import extract_text
import PyPDF2
import nltk
import re
import json
import cohere
import os
from dotenv import load_dotenv

load_dotenv()
COHERE_KEY = os.getenv('COHERE_KEY')

f = open('routes\skills.json')
data = json.load(f)
listOfSkills = []
for i in data:
    listOfSkills.append(i['name'].lower())


EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
 

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

router = APIRouter()

def extract_names(txt):
    person_names = []
 
    for sent in nltk.sent_tokenize(txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                person_names.append(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
 
    return person_names

def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)

def extract_skills(inp):
 
    # we create a set to keep the results in.
    found_skills = set()
 
    # we search for each token in our skills database
    for token in inp:
        if token.lower() in listOfSkills:
            found_skills.add(token)
 
    
 
    return list(found_skills)


# Getting all candidates
@router.get("/candidates")
async def get_candidate():
    candidates = list_serializer(collection_name.find())
    return candidates

# Adding a new candidate 
@router.post("/add")
async def post_candidate(resumeName: str, file: UploadFile = File(...)):
    try:
        reader = PyPDF2.PdfReader(file.file)
        raw = reader.pages[0].extract_text()
        names = extract_names(raw)
        name = names[0]
        email = extract_emails(raw)[0]
        languages = extract_skills(names[1:])
        keywords = names[1:]
        collection_name.insert_one(dict({"resume": resumeName,"name": name, "rawText":raw, "data":{"email": email, "skills": languages, "keywords" : keywords}}))

    except Exception as e:
        return {"message": e}
    finally:
        file.file.close()

@router.get("/query")
async def query_candidate(resumeName: str, query: str):
    candidate = list_serializer(collection_name.find({"resume": resumeName }))[0]["rawText"]
    co = cohere.Client(COHERE_KEY)
    message=f"Given the following candidate's data please answer this question:{query}. Here is the data: {candidate}"
    response = co.chat(
        message, 
        model="command", 
        temperature=0.45
    )
    return response.text

def lowercase(n):
  return n.lower()

@router.get("/match")
async def match(description: str, resumeName: str):
    candidate = list_serializer(collection_name.find({"resume": resumeName }))[0]["data"]["keywords"]
    keywordsForJob = extract_names(description)
    keywordsForCandidate = map(lowercase, candidate)
    matchedSkills=[]
    for skill in keywordsForJob:
        if skill.lower() in keywordsForCandidate:
            matchedSkills.append(skill)
    
    score = f"{int((len(matchedSkills)/len(keywordsForJob))*100)}%"

    return {"Match Score" : score, "Matched Skills": sorted(matchedSkills)}
    


# #updating a candidate
# @router.put("/{id}")
# async def put_candidate(id: str, candidate: Candidate):
#     collection_name.find_one_and_update({"_id": ObjectId(id)}, {"$set":dict(candidate)})

# #deleting candidate
# @router.delete("/{id}")
# async def delete_candidate(id: str):
#     collection_name.find_one_and_delete({"_id": ObjectId(id)})


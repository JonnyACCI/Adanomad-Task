## Demo Video 
https://www.youtube.com/watch?v=XGV9zHECcGc&ab_channel=JonathanS

## Usage
1. Firstly, make a MongoDB Atlas cluster if you do not have one already, and obtain your connection URI.
2. Secondly, signup for the Cohere API if you do not have an account already, and create a trial key (it is completely free). Save this somewhere as you can only see it once.
3. Make a `.env` file with the below information. Insert your respective keys without the quotations.
```
MONGO_URI=
COHERE_KEY=
```
4. Install the necessary libraries using the below commands. If you encounter error messages with `dotenv`, you may disregard them.
```
pip install fastapi uvicorn PyPDF2 nltk cohere pydantic "pymongo[srv]" dotenv
```

5. Now in the root directly, you may run the following command to run the server.

```
uvicorn main:app --reload
```

## Approach

I decided to make the backend with **FastAPI** as it offers greater speed than the likes of Flask. Moreover, since NoSQL was more fitting for the data this backend deals with, it is not optimal to use Django. 

I used FastAPI's built-in UploadFile class to enable file upload. From there, I extracted the text from the PDFs using PyPDF2. 

To parse through the resume for information, I used the Natural Language Toolkit which has a built-in set of words and offers the ability to detect names as well. I used this to extract the user's name, skills, and other keywords. In particular, for the skills, I used a large database of skills which can be found in the `skills.json` file in the `routes` directory.

To extract the email of the user, I simply used a regular expression.

To allow querying of the resume, I used Cohere's NLP model which is a cheaper alternative to OpenAI's GPT API. The temperature field in the call controls how creative and how much extra information the model provides for prompts. A higher value in the domain (0,1), indicates more creativeness.

For matching users, what I did was extract the skills from job description and calculate the percentage of those skills that are contained in the user's document in the database. This percentage is returned by the endpoint alongside an alphabetically sorted list of matched skills.

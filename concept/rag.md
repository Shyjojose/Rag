user queryy -> retriver -> context +query -> llm -> response

retiver has vector 

# Key concept 

Rag ground llm responses in auctual documents, reducing hallucination 

basic rag chain 
context 
prompt 
llm 
praser out put praser 

parellel input processing 

context comes from the retriver 
question is runnablePassThrough question that we got 
# prompt template 
-
answer based on 
{context}
question: {quesion}

# handling i dont know 

with instruction 
i dont have information about that in the provided context 

# i dont know system prompt

answer based only on the following context if the context dosent contain the ansewr say "i dont have information about it "
context:{context}
question:{question}

prompting is important 

# result is grounded 

retriver output 
page content here  source doc.pdf 
more content  source: guide.txt
faq context: source faq.md

format docs with sources 

enable citation in response. build trust 




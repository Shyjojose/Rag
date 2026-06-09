# chunking
chunking determine the rag quality 
fixed chunking 500 charecter-> it will split into two chunks and it can break in the middle 
semantic chunking-> the chunk splits at meaningul boundaries 
when you embedd chunks its act in isolation, this introduce mismatch = poor retrival 
# chunking variable 

two small chunk size optimal 200-1000
overlap 10-20% for overlap 
split boudatries-> instead of cutting at random cut (fixed) or cutting at paragraph/sentencs (resursive) and then we have semantic chunking ie cutting at meanigful boundaries 
content type - code legeal markdown each need different treatment 

# statergies to use 
fixed 
recursive (always used for the most part)
semantic   ( in case of legal document completely misses the retrival)
late -> embed first chunk later 


# decision framework 
--- fix size chunking just avoid its easy but never used for production 
--- recursive chunking -> try to split at oder of paragraph 80% of rag uses this for good balance with quality and speed 
    /n/n paragraph 
    /n good split 
    . split 
    , cluasees
    ' words 
    ' charecters warning dont use 

--- semantic chunking
split everything on meaning 
similarity score and when similarity score drops and start new rate limiting 
oAuth chunk1 and chunk2 clean topics bsed split. so not split at arbituary points 
accuracy is more speed is less 
--- late chunking 
traditional chunk- chunk documents and the document as a whole loose the understanding becasue each chunk which are changed into embededding and loose the boundary logic between document is chunked and they dont have relation to each other 
latechunking is embedding the whole document and then chunked into peices by pooling 

key insight 
chunk has no connection between them, the late chunking preserve that it will have 10 to 20 % 
all embedding model dosent support 
cutting edge model 
late chunking-> is the future 

chunking decision framework
start 
prototyping quickly -yes recursive 
no 
simple structured docs -yes recursive 
no 
quality criticla -yes semantic 
no 
complex topic shifting -yes semantic -no recursive 

general docs get recursive 
technical semantics auto 
code code splitter 
markdown md splitter 

# embedding dimensions 

text embedding-3-small 1536  dimensions relative size 
text-embedding-3-large 3072 dim
gemini embedding 768 dimensions free 
Bge-small 384 dimensions

-- difference between embedding vs chat models 

chat models -> you are using text in text out 
embedding model -> text in vector out 

phase 1 

load documents-chunk -embeding model - vector store

phase 2

query - embed query vector - search- retrive - generate - answer 

augmenting is making the llm smarter with our knowledge 


threee rules for produciton rag

- smae embedding model everyhwere ensure same models for indexing and query 
- embedding quality > quantity 
- test retrieval separately use specific evaluavation metrics 

# vector data base chroma 

app layer 

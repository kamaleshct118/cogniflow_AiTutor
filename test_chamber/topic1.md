
RAG

we apply rag when there is a need rag is external knowloge base,beacause of the llm hav ethe cut off knowledge and llm can hallucinate,here the rag is domain specific knowledge base use for external knowledge and avoid hallucination.

there is have lot of input source have like pdf,website,api so on.
now i explin using pdf source, the pdf have lot of pages and these are unstructured data.so we need to extract the data from pdf and store it in a database.
we use the extraction tools like pdfplumber,pymupdf,PyPDF2 and so on. this tool is not enough to extract the data from pdf because there is have lot of structure in pdf like tables,images,columns and so on.
so we use the parser tools like unstructured,pypdfium2 and so on. this tool is not enough to extract the data from pdf because there is have lot of structure in pdf like tables,images,columns and so on.

we cant give to dirrectly entire pdf or document to the llm because of the context window size limit. 

so we need to chunk the data into smaller chunks and store it in a
database.now each chunk is converted into vector using embeding model like embeddings small model.These vector are stored in a vector database like FAISS,Chroma,Pinecone and so on. 

now user question convert into vector using same embeding model.now the vector search in the vector database and find the similar vector.and return top k vector and their chunks.now combine all chunks and give it to the llm.

now the llm answer the question using the chunks.

now only retrive form the vector database, so llm cant hallucinate. the output is factual and accurate.


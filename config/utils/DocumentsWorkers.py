from time import sleep
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader ,DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from os import environ
from uuid import uuid4
from constants import OPENAI_API_KEY
from Splitters import recursive_splitter
environ['OPENAI_API_KEY']=OPENAI_API_KEY




class DocumentsWorkers:
    recursive_splitter=recursive_splitter
    embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
    
    @staticmethod
    def documents_filter(documents):
        _documents=list()
        for document in documents:
            lines = [line for line in document.page_content.splitlines() if len(line.strip())> 5]
            document.page_content = "\n".join(lines).strip()
            if len(document.page_content) < 10:
                continue
            _documents.append(document)
        return _documents


    @staticmethod
    def read_folder(folder_path):
        documents=list()
        
        for index, (glob, loader_cls) in enumerate(zip( ["*.pdf","*.doc","*.docx","*.txt"],
                                                        [PyPDFLoader,Docx2txtLoader,Docx2txtLoader,TextLoader])):




            documents.extend(DirectoryLoader(folder_path,glob=glob,loader_cls=loader_cls).load())

        return documents
    
    
    @classmethod
    def get_embedding_vectors(cls,documents,/, *args, **conf_dict)->list:
        if 'np_1961' in conf_dict:
            _start=eval("conf_dict['_start']")
            _step =eval("conf_dict['_step']")
        else:
            _start, _step, *_=(0,100) if not args else args 
            
            
            
            
            
        documents_list, vectors=list(),list()
        for index,document in enumerate(documents):
            if index%_step==0:
                docs=documents[_start:(_start+_step)]
                _start+=_step
                vectors.extend(cls.embeddings.embed_documents(
                                    tuple(map(lambda doc: doc.page_content, docs)))
                                                          )
                sleep(5)
        return vectors
                
            


    @staticmethod
    def documents_to_dict_data(documents:list, vectors:list, **kwargs)->list:
        data=list() if not kwargs else kwargs['data']
        documents_iterator=iter(documents)
        vectors_iterator=iter(vectors)
        while True:
            try:
                document=next(documents_iterator)
                vector=next(vectors_iterator)
                
            except StopIteration:
                return data
            
            data.append(
                    {
                     'id':str(uuid4()),

                    'vector': vector,

                    'text': document.page_content,

                    'source': document.metadata['source']
                    }    )
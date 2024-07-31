


import sys
from os import environ



import numpy as np
from pandas import DataFrame
from pandas import Series
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from pymilvus import (MilvusClient,
                      CollectionSchema,
                      FieldSchema,
                      DataType,
                      utility,
                      db,
                      connections)

from Terminal import terminal_write
from DocumentsWorkers import DocumentsWorkers
from Splitters import recursive_splitter
from Status import StatusAssigner
from constants import OPENAI_API_KEY
from constants import persist_directory

environ['OPENAI_API_KEY']=OPENAI_API_KEY
embeddings = OpenAIEmbeddings(model='text-embedding-3-large')



# from pymilvus.model.dense.openai import OpenAIEmbeddingFunction

# openai_ef = OpenAIEmbeddingFunction(
#     model_name='text-embedding-3-large', # Specify the model name
#     api_key=OPENAI_API_KEY, # Provide your OpenAI API key
#     dimensions=3072 # Set the embedding dimensionality
# )
# embedding_texts=openai_ef.encode_documents(documents=tuple(map(lambda _data: _data['text'], data)))






class MilvusControll(StatusAssigner):
    _client = MilvusClient(uri="http://localhost:19530")
    
    
    def __init__(self, collection_name:str)->None:
        self.__collection_name = collection_name
        self.client = MilvusClient(uri="http://localhost:19530")


    @property
    def collection_name(self):
        return self.__collection_name
    
    @collection_name.setter
    def collection_name(self, name):
        if name not in self.client.list_collections():
            raise ValueError("Collection not found ")
        self.__collection_name=name
        
    
    @classmethod
    def drop_all_conf(cls, conf:str)->None:
        if conf in ['collection', 'collections']:
            [cls._client.drop_collection(_collection_name) for _collection_name in cls._client.list_collections()]
        elif conf =='alias':
            [cls._client.drop_alias(alias=alias) for alias in list(cls._client.list_aliases().values())[0]]
        else:
            raise ValueError('Problem in conf name !!!')
        terminal_write(f'---Drop all {conf}')

        
    
    def create_collection(self):
        
        schema = self.client.create_schema(auto_id=False,
                                           enable_dynamic_field=True)
        
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=36)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=36)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=3072)
        
        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name="vector",metric_type="COSINE",)
        [index_params.add_index(field_name=field_name) for field_name in ['id',
                                                                          'source',
                                                                          'text']]
        self.client.create_collection(collection_name=self.collection_name,
                                      schema=schema,
                                      index_params=index_params)
        
        
                
    def create_alias(self, alias_name:str)->dict:
        self.client.create_alias(collection_name=self.collection_name,
                                 alias=f"{self.collection_name}_{alias_name}")
        return self.good_status()
        
        
        
        
        


        
        
    def insert(self,data:list, partition_name:str='_default')->dict:
        return self.client.insert(         collection_name=self.collection_name,
                                           data=data,
                                           partition_name = partition_name )
    
    
        
    def upsert(self, data:list)->dict:
        return self.client.upsert(
                                    collection_name=self.collection_name,
                                    data=data)




    
    def similarity_search(self, text:str, limit:int=10)->list:
        embed_query_vector=embeddings.embed_query(text=text)
        outputs=self.client.search(
                                    collection_name=self.collection_name,    
                                    data=[embed_query_vector],                
                                    limit=limit)[0]

        ids=list(map(lambda output:output['id'],outputs))
        return self.client.get(
                    collection_name=self.collection_name,
                    ids=ids)
    
    
    def search_data_by_filter(self, filter_query:str=''):
        return self.client.query(
                    collection_name=self.collection_name, 
                    filter=filter_query) #       "id in [4,5,6]"

    def delete_data(self, filter_query:str='',**kwargs)->dict:
        """ write how to delete using a filter or ids """
        filter_query=filter_query if not kwargs else f"id in {kwargs['ids']}"
        return self.client.delete(collection_name=self.collection_name, filter=filter_query)
    
    

        



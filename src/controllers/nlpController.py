from .BaseController import BaseController
from models.db_schemes import project
from stors .LLM .llmEnums import DecomentTypeEnums
from models.db_schemes.data_chunk import DataChunk 
import json
from tqdm import tqdm
class NLPController(BaseController):
    def __init__(self, ganeration_client,vector_db_client, embedding_client,templete_parser):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.ganeration_client = ganeration_client
        self.templete_parser= templete_parser
    def collection_name(self, project_id: str) -> str:
        return f"nlp_collection_{project_id}".strip()
    

    def reset_vector_db_collection(self, project: project):
        collection_name = self.collection_name(project_id=project.project_id)
        return self.vector_db_client.deleteCollection(collection_name=collection_name)
    

    def get_vector_db_collection_info(self, project: project):
        collection_name = self.collection_name(project_id=project.project_id)
        collection_info=self.vector_db_client.getCollectionInfo(collection_name=collection_name)
        return json.loads(
            json.dumps(
                collection_info,
                default=lambda o: o.__dict__
                )
            )
    

    def index_vector_db (self ,project:project,chunks:list[DataChunk],chunk_ids:list[int],do_reset:bool=False):
        collection_name = self.collection_name(project_id=project.project_id)
        # embedding_size = self.embedding_client.get_embedding_size(model_id=project.embedding_model_id)
        # self.vector_db_client.createCollection(collection_name=collection_name, embedding_size=embedding_size, do_reset=project.reset_vector_db)
        texts = [chunk.chunk_txt for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]
       
       
      
            
        # generate embeddings for texts
        vectors = []
        for idx in tqdm(range(0, len(texts), 10), desc="Generating embeddings", unit="text"):
            batch_texts = texts[idx:idx + 10]
            vec = self.embedding_client.embedding_text(
                text=batch_texts,
                decument_type=DecomentTypeEnums.DOCUMENT.value,
            )
            vectors.extend(vec if vec else [None] * len(batch_texts))

        # validate embeddings
        if not vectors or len(vectors) == 0:
            return False

        # determine actual embedding dimension from produced vectors
        try:
            actual_dim = len(vectors[0]) if vectors[0] is not None else None
        except Exception:
            actual_dim = None

        if actual_dim is None:
            return False

        # ensure all vectors have the same dimension; drop any that don't
        filtered_texts = []
        filtered_metadata = []
        filtered_vectors = []
        filtered_ids = []
        for i, v in enumerate(vectors):
            if v is None:
                continue
            if len(v) != actual_dim:
                continue
            filtered_vectors.append(v)
            filtered_texts.append(texts[i])
            filtered_metadata.append(metadata[i])
            filtered_ids.append(chunk_ids[i] if chunk_ids is not None and i < len(chunk_ids) else None)

        if len(filtered_vectors) == 0:
            return False

        # create collection with the actual embedding dimension (use actual_dim)
        _ = self.vector_db_client.createCollection(
            collection_name=collection_name, embedding_size=actual_dim, do_reset=do_reset
        )

        _ = self.vector_db_client.insertMany(
            record_ids=filtered_ids,
            collection_name=collection_name,
            text=filtered_texts,
            vector=filtered_vectors,
            metadate=filtered_metadata,
        )
        return True
    def search_vector_db(self, project: project, text: str, limit: int = 5):
        collection_name = self.collection_name(project_id=project.project_id)
        query_vector = self.embedding_client.embedding_text(
            text=text, decument_type=DecomentTypeEnums.DOCUMENT.value
        )

        if not query_vector or len(query_vector) == 0:
            return False

        # inspect existing collection info to validate vector sizes
        try:
            collection_info = self.vector_db_client.getCollectionInfo(collection_name=collection_name)
        except Exception:
            collection_info = None

        collection_size = None
        if collection_info:
            # collection_info may be an object or dict depending on client; try common fields
            try:
                info = json.loads(json.dumps(collection_info, default=lambda o: o.__dict__))
                vc = info.get("vectors_config") or info.get("params") or info.get("vectors")
                if isinstance(vc, dict):
                    collection_size = vc.get("size") or (vc.get("vectors") or {}).get("size")
            except Exception:
                collection_size = None

        if collection_size is not None and len(query_vector) != collection_size:
            return {"error": "dimension_mismatch", "message": f"Query embedding dimension {len(query_vector)} does not match collection dimension {collection_size}"}

        search_results = self.vector_db_client.searchByVector(
            collection_name=collection_name, query_vector=query_vector, limit=limit
        )
        if not search_results:
            return False

        return search_results
    
    def ansewer_rag_query(self, project: project, query: str,limit: int = 10):
        ansewer,full_prompt,chat_history=None,None,None

        search_results = self.search_vector_db(project=project, text=query, limit=limit)
       
        if not search_results or len(search_results) == 0:
            return ansewer,full_prompt,chat_history

        system_prompt=self.templete_parser.get_rag_templet("rag","system_prompt")

        # decoment_prompts=[ ]
        # for idx,doc in enumerate(search_results):
        #     decoment_prompts.append(self.templete_parser.get_decoment_prompt("rag","decoment_prompt",{
        #         "doc_no":idx+1,
        #         "chunk_text":doc.document_text}))

        decoment_prompts="\n".join([
            self.templete_parser.get_rag_templet("rag","decoment_prompt",{
                "doc_no":idx+1,
                "chunk_text":doc.document_text})
            for idx,doc in enumerate(search_results)
        ])

        footer_prombet=self.templete_parser.get_rag_templet("rag","footer_prompt")

        chat_history=[
            self.ganeration_client.construct_prompt(system_prompt, self.ganeration_client.enums.SYSTEM.value),
            # self.ganeration_client.construct_prompt(decoment_prompts, self.ganeration_client.enums.user.value),
            # self.ganeration_client.construct_prompt(footer_prombet, self.ganeration_client.enums.user.value),
            # self.ganeration_client.construct_prompt(query, self.ganeration_client.enums.user.value),
        ]
        full_prompt=f"{decoment_prompts}\n{footer_prombet}\nQuestion: {query}"
        ansewer=self.ganeration_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
            
        )
        return ansewer,full_prompt,chat_history
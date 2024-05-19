from haystack.nodes import TextConverter, PreProcessor
from haystack.nodes import PreProcessor
from haystack.pipelines import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from envkey import getOpenAPIkey
openai_api_key = getOpenAPIkey()


def PrepareDatastore():
    FileName = "output-onlinejsontools.txt"
    converter = TextConverter(
        remove_numeric_tables=True, valid_languages=["en"])
    doc_docx = converter.convert(file_path=f"{FileName}", meta=None)[0]

    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=False,
        split_by="word",
        split_length=100,
        split_respect_sentence_boundary=True,
    )
    docs_default = preprocessor.process([doc_docx])
    print(f"n_docs_input: 1\nn_docs_output: {len(docs_default)}")

    document_store = InMemoryDocumentStore(use_bm25=True)
    document_store.write_documents(docs_default)
    return document_store


def PrepareRetriver(document_store):
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    # Important:
    # Now that we initialized the Retriever, we need to call update_embeddings() to iterate over all
    # previously indexed documents and update their embedding representation.
    # While this can be a time consuming operation (depending on the corpus size), it only needs to be done once.
    # At query time, we only need to embed the query and compare it to the existing document embeddings, which is very fast.
    document_store.update_embeddings(retriever)
    return retriever


def PrepareRagNode():
    rag_prompt = PromptTemplate(
        prompt=""" Act like a indian government offical, who came to educate the teenagers on sexual awarness, and have a proper information provided in text below. Now, Synthesize a comprehensive answer for the given question under the gudielines of Indian laws.
                                Start your answer by mentioning the topic from which you are giving the answer mentioned in the text, followed by the question you understood and then the response
                                Provide a clear and concise response that summarizes the key points and information presented in the text and your answer should be no longer than 50 words.
                                If question is not clear or seams to be incomplete, ask question back to user to understand what they are asking, it a strict command not to answer any incomplete questions
                                \n\n Related text: {join(documents)} \n\n Question: {query} \n\n Answer:""",
        output_parser=AnswerParser(),
    )
    prompt_node = PromptNode(model_name_or_path="gpt-3.5-turbo",
                             api_key=openai_api_key,
                             max_length=500,
                             model_kwargs={"temperature": 0.1},
                             default_prompt_template=rag_prompt,
                             )
    return prompt_node


def PrepareRepharseNode():
    rephrase_prompt = PromptTemplate(
        prompt=""" Understand the semantic meaning of the question asked and rephrase the question as a medical practioner, so common people can understand the given question in min 25 words.
        strict guideline, you have to just give the rephrased question as output
        \n\n Question: {query} \n\n Answer:""",
        # output_parser=AnswerParser(),
    )
    rephrase_prompt_node = PromptNode(model_name_or_path="gpt-3.5-turbo",
                                      output_variable="fquery",
                                      api_key=openai_api_key,
                                      max_length=500,
                                      model_kwargs={"temperature": 0.1},
                                      default_prompt_template=rephrase_prompt,
                                      )
    return rephrase_prompt_node

def BuildPipline(prompt_node, retriever):
    pipe = Pipeline()
    pipe.add_node(component=retriever, name="retriever", inputs=["Query"])
    pipe.add_node(component=prompt_node, name="prompt_node", inputs=["retriever"])
    return pipe

# ===============

documentstore = PrepareDatastore()
retriever = PrepareRetriver(documentstore)
ragNode = PrepareRagNode()
repharseNode = PrepareRepharseNode()
pipe = BuildPipline(prompt_node=ragNode, retriever=retriever)

def ProcessQuery(user_prompt):
    print("\nUser:\n", user_prompt)
    print("----\n")
    testResult = repharseNode.run(query=user_prompt)
    rephrasedQ = testResult[0]['fquery'][0]
    print("\nRephrased Question:\n", rephrasedQ)
    print("----\n")
    output = pipe.run(rephrasedQ)
    print(output["answers"][0].answer)
    print("----\n")
    return output





def getlm_client():
    return openai.OpenAI(api_key="opeanai_api_key")


lm_client = getlm_client()





@app.route("/level1/stream")
@login_required
@user_activity_tracker
def level1_stream():
    global p1, l1_text, layer_1
    existing_data = readAndWriteJsonData("configu.json", "r")

    layer1 = existing_data["layer1"]

    openaiKey = existing_data["openaiKey"]


    dbclient = weaviate_client(layer1["layer1URL"],layer1["layer1AuthKey"],openaiKey)


    print(layer1, "layer 1  dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    # Load the configuration to get className1
    data = readAndWriteJsonData("configu.json", "r")
    config_data = data.get("layer1", demo_configuration("layer1"))

    email = manage_json("read", "instanceRunning")
    print(f"Using email for operations: {email}")  # Debug print

    data_file_path = f"tag_for_each_sentence_{email}_layer1.json"
    print(f"Looking for file: {data_file_path}")  # Debug print

    class_name1 = config_data["classNamelayer1"]
    print(class_name1, "class Name is given")
    # Capitalize the first letter of className1
    ClassName1 = class_name1.capitalize()
    print(ClassName1, "what is this mannnnnnnnn")

    synms = "No synonyms"

    query_string, reasoning_string = get_syn_query_and_reasoning_string(
        session["transcription"].lower(), synms
    )

    try:
        context = []
        metadata = []
        chunk_ids = []

        process_as_image = config_data["process_image"]

        if process_as_image:

            worddata = read_json_file(data_file_path)
            print("userid ti e chose hereeeeeeee", email)
            synonyms = manage_json("read", "synonyms")
            if synonyms:
                synms = synonyms

            tags = ask_gpt_tags(query_string.lower(), synms)
            tags = [tag.lower() for tag in tags]
            words = word_tokenize(query_string.lower())
            stoptags = [
                word for word in words if word.lower() not in stopwords.words("english")
            ]
            tags = update_strings_list(stoptags, tags)
            tags = remove_characters_from_list(tags, ["?", ".", "!"])
            most_closest = get_relevant_tags(tags, class_name1, ClassName1)
            print(class_name1, ClassName1, "checknndndndqkdnndndndndnd")

            print(most_closest, "most_closest -------------->>>>>")

            context, metadata = get_all_sentences(most_closest, worddata, "layer1")

        else:
            print("..")
            context, metadata = qdb(
                query_string,
                dbclient,
                class_name1,
                ClassName1,
                chunk_id=1,
                limit=20,
            )

        sufficient = False
    except Exception as e:
        print("\n\n\nError:    ", e)
        update_logs(e)

    email = manage_json("read", "instanceRunning")

    context_Length = len(context)

    print(context_Length, "length of context before filtering ------------")

    context = join_strings_with_ids(context)


    if(context_Length>100):
        print(context_Length,'context length is .....')

        chunk_ids_list = make_small_chunk_of_context(context,500)


        for chunk in enumerate(chunk_ids_list):
            ids = filter_information(reasoning_string,chunk)
            if(len(ids)==0):
                continue
            chunk_ids = chunk_ids + ids


        print(len(chunk_ids), "length of context after filtering ------------")


        new_context,new_metadata = get_accurate_context_and_metadata(chunk_ids,context,metadata)

        context = new_context

        metadata = new_metadata



    try:

        filename = f"Layer_1_file_{email}/file_info_1.json"

        question = (reasoning_string,)
        context = context
        addition = manage_json("read", "p1")
        filename = f"Layer_1_file_{email}/file_info_1.json"
        intro_msg = manage_json("read", "l1")
        user_message = "Question: \n\n" + question[0] + "\n\n\nContext: \n\n" + context

        system_message = "You will be given context from several pdfs, this context is from several chunks, rettrived from a vector DB. each chunk will have a chunk id above it. You will also be given a question. Formulate an answer, ONLY using the context, and nothing else. provide in-text citations within square brackets []  at the end of each sentence, right after each fullstop. The citation number represents the chunk id that was used to generate that sentence. Do Not bunch multiple citations in one bracket. Use seperate brackets [] for each digit. {} Return the response along with a boolean value indicating if the information from the context was enough to answer the question. Return true if it was, False if it wasnt. Return the response, which is th answer to the question asked".format(
            addition
        )

        print("test2")
        msg = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        print("\n\n\n\n\n\nChecking for response\n\n\n\n\n\n")

        question = reasoning_string
        context = context
        metadata = metadata
        addition = manage_json("read", "p1")
        filename = f"Layer_1_file_{email}/file_info_1.json"
        print("test3")
        messages = msg
        max_tokens = 4000
        temperature = 0.0
        seed = 1
        function_call = "auto"
        print("test4")

        with open("metadata_temp.json", "w") as file:
            json.dump(metadata, file)

    except Exception as e:
        print("exception in simple stream 1", e)
    try: 
        custom_functionsz = get_custom_functionsz()

        def internal_method():
            ans = ""
            capturing = False
            stream_message = ""
            lm_client = getlm_client()
            response = lm_client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                seed=seed,
                functions=custom_functionsz,
                function_call=function_call,
                stream=True,
            )
            print("response is", response)
            for chunk in response:
                temp = ""
                try:
                    if chunk.choices[0].delta.function_call.arguments is not None:
                        ans += chunk.choices[0].delta.function_call.arguments
                        temp += chunk.choices[0].delta.function_call.arguments

                        stream_message,answer, capturing = make_line(temp,capturing,stream_message,intro_msg)
                        
                        data = {"response": answer, "sufficient": False}

                        json_data = json.dumps(data)
                        yield f"data: {json_data}\n\n"
                except Exception as e:
                    print("exception in chunk call", e)

            final_ans = "".join(ans)


            reply = ""
            reply += "\n\n"
            reply += intro_msg
            reply += "\n\n"

            resp_json = json.loads(final_ans)

            item_list = resp_json["item_list"]
            reply += resp_json["response_answer"]

            with open(filename, "r") as file:
                files_metadata = json.load(file)

            metadata_local = ["dummy_addition_in_ordr_to_reove_zero_index"] + metadata


            try:
                print(item_list, "item list -----------\n     ")
                cits = ["www.google.com"] * (max(item_list) + 4)
                unique_metadata = set()
                for item in item_list:
                    print(item, "item in itemList \n\n\n\n\n")
                    citation_name = replace_in_string(
                        metadata[item - 1].split(".png")[0]
                    )
                    if citation_name not in unique_metadata:
                        unique_metadata.add(citation_name)
                        reply += "\n"
                        reply += "[{}]".format(item)
                        reply += citation_name

                    for filedata in files_metadata:

                        name = filedata["name"].split(".docx")[0]
                        name = name.split(".pptx")[0]
                        name = name.split(".pdf")[0]
                        mimeType = filedata["mimeType"]
                        file_id = filedata["id"]
                        if name in metadata_local[item]:
                            if (
                                mimeType
                                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            ):
                                cits[item] = generate_google_docs_url(file_id)
                            else:
                                cits[item] = generate_google_drive_url(file_id)

                print(
                    cits,
                )
                lst = "\n\n\n list_of_citations = " + str(cits)

                lst = lst.replace("'", '"')
                reply += lst
            except Exception as e:
                print("Error processing item list and metadata:", e)
                pass

            data = {"response": reply, "sufficient": False, "endOfStream": True}
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"

        return Response(
            internal_method(),
            content_type="text/event-stream",
        )

    except Exception as e:
        print("Exception in simple stream", e)
        data = {"response": "Error.", "sufficient": False}
        json_data = json.dumps(data)
        resp = f"data: {json_data}\n\n"
        return Response(resp, content_type="text/event-stream")






@app.route("/level2/stream")
@login_required
@user_activity_tracker
def level2_stream():
    global p1, l1_text, layer_2
    existing_data = readAndWriteJsonData("configu.json", "r")


    layer2 = existing_data["layer2"]


    openaiKey = existing_data["openaiKey"]


    dbclient = weaviate_client(layer2["layer2URL"],layer2["layer2AuthKey"],openaiKey)

    # Load the configuration to get className1
    data = readAndWriteJsonData("configu.json", "r")

    config_data = data.get("layer2", demo_configuration("layer2"))

    email = manage_json("read", "instanceRunning")
    print(f"Using email for operations: {email}")  # Debug print

    data_file_path = f"tag_for_each_sentence_{email}_layer2.json"

    class_name1 = config_data["classNamelayer2"]
    print(class_name1, "class Name is given")
    # Capitalize the first letter of className1
    ClassName1 = class_name1.capitalize()
    print(ClassName1, "what is this mannnnnnnnn")

    synms = "No synonyms"

    query_string, reasoning_string = get_syn_query_and_reasoning_string(
        session["transcription"].lower(), synms
    )

    try:
        context = []
        metadata = []
        qdbcontext = ""
        qdbmetadata = []
        chunk_ids = []

        process_as_image = config_data["process_image"]

        if process_as_image:

            worddata = read_json_file(data_file_path)
            print("userid ti e chose hereeeeeeee", email)
            synonyms = manage_json("read", "synonyms")
            if synonyms:
                synms = synonyms

            tags = ask_gpt_tags(query_string.lower(), synms)
            tags = [tag.lower() for tag in tags]
            words = word_tokenize(query_string.lower())
            stoptags = [
                word for word in words if word.lower() not in stopwords.words("english")
            ]
            tags = update_strings_list(stoptags, tags)
            tags = remove_characters_from_list(tags, ["?", ".", "!"])
            most_closest = get_relevant_tags(
                tags, class_name1, ClassName1
            )  # Updated to pass the dynamic class names

            context, metadata = get_all_sentences(most_closest, worddata, "layer2")


            
        else:
            print("..")
            context, metadata = qdb(
                query_string,
                dbclient,
                class_name1,
                ClassName1,
                chunk_id=1,
                limit=20,
            )

        sufficient = False
    except Exception as e:
        print("\n\n\nError:    ", e)
        update_logs(e)
        chunk_ids = []

    email = manage_json("read", "instanceRunning")


    context_Length = len(context)

    print(context_Length, "length of context before filtering ------------")

    context = join_strings_with_ids(context)


    if(context_Length>100):
        print(context_Length,'context length is .....')

        chunk_ids_list = make_small_chunk_of_context(context,500)


        for chunk in enumerate(chunk_ids_list):
            ids = filter_information(reasoning_string,chunk)
            if(len(ids)==0):
                continue
            chunk_ids = chunk_ids + ids

        print(chunk_ids,'chunk id got from filter functions')
        
        print(len(chunk_ids), "length of context after filtering ------------")


        new_context,new_metadata = get_accurate_context_and_metadata(chunk_ids,context,metadata)

        context = new_context

        metadata = new_metadata



    try:

        filename = f"Layer_2_file_{email}/file_info_1.json"

        question = (reasoning_string,)
        context = context
        addition = manage_json("read", "p2")
        metadata = metadata
        filename = f"Layer_2_file_{email}/file_info_1.json"
        intro_msg = manage_json("read", "l2")
        user_message = "Question: \n\n" + question[0] + "\n\n\nContext: \n\n" + context

        system_message = "You will be given context from several pdfs, this context is from several chunks, rettrived from a vector DB. each chunk will have a chunk id above it. You will also be given a question. Formulate an answer, ONLY using the context, and nothing else. provide in-text citations within square brackets []  at the end of each sentence, right after each fullstop. The citation number represents the chunk id that was used to generate that sentence. Do Not bunch multiple citations in one bracket. Use seperate brackets [] for each digit. {} Return the response along with a boolean value indicating if the information from the context was enough to answer the question. Return true if it was, False if it wasnt. Return the response, which is th answer to the question asked".format(
            addition
        )
        msg = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        messages = msg
        max_tokens = 4000
        temperature = 0.0
        seed = 1
        function_call = "auto"
        print("test4")
        with open("metadata_temp.json", "w") as file:
            json.dump(metadata, file)

    except Exception as e:
        print("exception in simple stream 1", e)
    try:

        
        def internal_method():
            custom_functionsz = get_custom_functionsz()
            ans = ""
            capturing = False
            stream_message = ""
            lm_client = getlm_client()
            response = lm_client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                seed=seed,
                functions=custom_functionsz,
                function_call=function_call,
                stream=True,
            )
            print("response is", response)
            for chunk in response:
                temp = ""
                try:
                    if chunk.choices[0].delta.function_call.arguments is not None:
                        ans += chunk.choices[0].delta.function_call.arguments
                        temp += chunk.choices[0].delta.function_call.arguments

                        stream_message,answer, capturing = make_line(temp,capturing,stream_message,intro_msg)
                        
                        data = {"response": answer, "sufficient": False}

                        json_data = json.dumps(data)
                        yield f"data: {json_data}\n\n"
                except Exception as e:
                    print("exception in chunk call", e)

            final_ans = "".join(ans)

            reply = ""
            reply += "\n\n"
            reply += intro_msg
            reply += "\n\n"

            resp_json = json.loads(final_ans)

            item_list = resp_json["item_list"]
            reply += resp_json["response_answer"]

            with open(filename, "r") as file:
                files_metadata = json.load(file)

            metadata_local = ["dummy_addition_in_ordr_to_reove_zero_index"] + metadata


            try:
                print(item_list, "item list -----------\n     ")
                cits = ["www.google.com"] * (max(item_list) + 4)
                unique_metadata = set()
                for item in item_list:
                    print(item, "item in itemList \n\n\n\n\n")
                    citation_name = replace_in_string(
                        metadata[item - 1].split(".png")[0]
                    )
                    if citation_name not in unique_metadata:
                        unique_metadata.add(citation_name)
                        reply += "\n"
                        reply += "[{}]".format(item)
                        reply += citation_name

                    for filedata in files_metadata:

                        name = filedata["name"].split(".docx")[0]
                        name = name.split(".pptx")[0]
                        name = name.split(".pdf")[0]
                        mimeType = filedata["mimeType"]
                        file_id = filedata["id"]
                        if name in metadata_local[item]:
                            if (
                                mimeType
                                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            ):
                                cits[item] = generate_google_docs_url(file_id)
                            else:
                                cits[item] = generate_google_drive_url(file_id)

                print(
                    cits,
                )
                lst = "\n\n\n list_of_citations = " + str(cits)

                lst = lst.replace("'", '"')
                reply += lst
            except Exception as e:
                print("Error processing item list and metadata:", e)
                pass

            data = {"response": reply, "sufficient": False, "endOfStream": True}
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"


 
        return Response(
            internal_method(),
            content_type="text/event-stream",
        )

    except Exception as e:
        print("Exception in simple stream", e)
        data = {"response": "Error.", "sufficient": False}
        json_data = json.dumps(data)
        resp = f"data: {json_data}\n\n"
        return Response(resp, content_type="text/event-stream")



def ask_gpt_smart_chunk(question):
    system_message = "You are a smart chunker. You will be given content from a slide/document page. You need to return the data, but divided into chunks - meaning, the chunk you return must encapsulate complete information. You are allowed to return as many chunks as you like. But, you must cover the entire information. The reasons is that I will be feeding this into a vector database for semantic retrival of vectors. By feeding an entire page, the similarity scores are very low for specific queries that are only a fraction of the larger page. But, if I were to auto chunk it by 100 or some words, then there are cases where information could be cut off, etc, Therefore, you must return a list of strings. This is called smart chunking. Finally, remeber, what you return, when read, must preserve context. Just returning names, or sentences without any indication of the context or what they represent will be useless. Each chunk must represent the heading it was pulled from, so that when we look at it we know exactly the central context from where it was derived from. it should be so good that a reader must be able to put back the original text be peicing the chunks together. that is how good it should be. Each chunk MUST contain the heading or subheading from where it was taken from. Otherwise, it will make absolutely no sense when looking at it seperately."
    user_message = "content from page from document below: \n" + question
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("-----------------------")
    lm_client = getlm_client()
    response = lm_client.chat.completions.create(
        model="gpt-4",
        messages=msg,
        max_tokens=500,
        temperature=0.0,
        functions=smart_function,
        function_call="auto",
    )
    reply = response.choices[0].message.content
    try:
        reply = ast.literal_eval(reply)
    except:
        try:
            reply = json.loads(response.choices[0].message.function_call.arguments)[
                "item_list"
            ]
            print(reply)
        except:
            print(reply)
            reply = []

    return reply





def ask_gpt_tags(question, synonums = "No synonyms"):
    system_message = "You will be given a sentence. You must behave as an extremly smart named entity recognition software. Your job is to extract ALL of the entitties from the sentence. Company names, people names, designations, and all other unique nouns etc. A list of synonyms also will be provided. Your  I will use these tags to filter data. If any of the entities are in the synonums, then you must also include all of the synonyms along with the other entiies you extracted. return a list of string tags."
    user_message = "Sentence: \n" + question + "\n\n Synonyms: \n" + f"{synonums}"
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("-----------------------")


    response = lm_client.chat.completions.create(
        model="gpt-4",
        messages=msg,
        max_tokens=500,
        temperature=0.0,
        functions=custom_functions_tag,
        function_call="auto",
    )

    reply = response.choices[0].message.content
    print("TAGS repomnse: ",response)
    try:
        reply = ast.literal_eval(reply)
        print("Regular text to list.")
        try:
            reply = reply["item_list"]
        except:
            pass
        print(reply)
    except:
        try:
            reply = json.loads(response.choices[0].message.function_call.arguments)[
                "item_list"
            ]
            print(reply)
        except Exception as e:
            print(e)
            reply = []
    return reply





def initiate_clients():
    global openai_flag, layer_1_flag, layer_2_flag, lm_client, layer_1, layer_2, error_admin_msg, loading_status
    data = readAndWriteJsonData("configu.json", "r")

    if not data:
        print("Configuration data not found. Please check the configu.json file.")
        error_admin_msg = "Configuration data not found."
        progress_log(error_admin_msg)
        return

    config_data = data.get("layer1", demo_configuration("layer1"))
    config_data1 = data.get("layer2", demo_configuration("layer2"))

    # Initialize error flags
    openai_flag = False
    layer_1_flag = False
    layer_2_flag = False
    error_admin_msg = ""

    # Check OpenAI API Key
    if "openaiKey" not in data or not data["openaiKey"]:
        openai_flag = True
        error_admin_msg += "Please check your OpenAI API KEY.\n"
    else:
        try:
            openai.api_key = data["openaiKey"]
            print(openai.api_key, "api key openai.......................")
            
            lm_client = openai.OpenAI(api_key=data["openaiKey"])
            msg = [
                {"role": "system", "content": "system_message"},
                {"role": "user", "content": "user_message"},
            ]

            response = lm_client.chat.completions.create(
                model="gpt-4",
                messages=msg,
                max_tokens=1000,
                temperature=0.0,
            )
            loading_status = "LLM Client Working..."
            print("lm_client working")
        except Exception as e:
            openai_flag = True
            print(f"lm_client not working: {e}")
            error_admin_msg += "Please check your OpenAI API KEY.\n"

    # Check Layer 1 Configuration
    if not config_data.get("layer1URL"):
        layer_1_flag = True
        error_admin_msg += "Please check your Layer_1 URL.\n"
    if not config_data.get("layer1AuthKey"):
        layer_1_flag = True
        error_admin_msg += "Please check your Layer_1 Auth Key.\n"

    if not layer_1_flag:
        try:
            layer_1 = weaviate_client(config_data["layer1URL"], config_data["layer1AuthKey"], data["openaiKey"])
            if layer_1 is None:
                layer_1_flag = True
                error_admin_msg += "Invalid Layer_1 URL or Auth Key.\n"
            else:
                print("layer 1 working", layer_1)
                loading_status = "layer 1 working..."
        except Exception as e:
            layer_1_flag = True
            print(f"Layer_1 not working: {e}")
            error_admin_msg += "Please check your Layer_1 configuration.\n"

    # Check Layer 2 Configuration
    if not config_data1.get("layer2URL"):
        layer_2_flag = True
        error_admin_msg += "Please check your Layer_2 URL.\n"
    if not config_data1.get("layer2AuthKey"):
        layer_2_flag = True
        error_admin_msg += "Please check your Layer_2 Auth Key.\n"

    if not layer_2_flag:
        try:
            layer_2 = weaviate_client(config_data1["layer2URL"], config_data1["layer2AuthKey"], data["openaiKey"])
            if layer_2 is None:
                layer_2_flag = True
                error_admin_msg += "Invalid Layer_2 URL or Auth Key.\n"
            else:
                loading_status = "layer 2 working..."
                print("layer 2 working")
        except Exception as e:
            layer_2_flag = True
            print(f"Layer_2 not working: {e}")
            error_admin_msg += "Please check your Layer_2 configuration.\n"

    # Final status check
    if not openai_flag and not layer_1_flag and not layer_2_flag:
        loading_status = "Ready to use..."
        print("Ready to use")
        progress_log(loading_status)
    else:
        progress_log(error_admin_msg)





def test_openai_key(key, question="what is the capital of India?"):
    data = readAndWriteJsonData("configu.json", "r")
    lm_client = openai.OpenAI(api_key=data["openaiKey"])
    try:
        response = lm_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}],
            max_tokens=50
        )
        reply = response.choices[0].message.content
        if reply:  # This check ensures there is a meaningful response
            return True, "OpenAI key working successfully."
    except Exception as e:
        error_message = str(e).lower()
        if "authentication" in error_message:
            return False, "OpenAI key expired or invalid."
        return False, "Error with OpenAI key: " + str(e)
    return False, "Unexpected error occurred"


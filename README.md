

AI Sales chatbot is based on the state-of-the-art OpenAI GPT-3/GPT-4 model. It ensures human-like interaction by avoiding hallucinations and refraining from referencing its AI nature. The chatbot is integrated with WhatsApp, enabling incoming leads and new customers to interact, ask questions, and be qualified as high intent leads. It leverages a knowledge base to learn and provide accurate answers to customer inquiries. The chatbot possesses long-term memory capabilities, allowing it to remember previous client conversations, including communication details, rapport, and answers to questions.
Steps:

    Chatbot based on openAI GPT-3.5 Turbo/GPT-4 model.
    Human based interaction, no hallucinations and no reference to being an LLM/AI/Bot.
    Connection to WhatsApp for incoming leads/new customers to be able to interact/ask questions/be qualified as high intent leads.
    AI Bot will learn a knowledge base and answer questions accordingly.
    Long term memory of clients spoken to previously, and memory of current conversation.
        Remembering communication / rapport (names, answers to questions)
        Qualification score
        No repetition of questions
    Replies via whatsapp with a humanization element (Typing indicator, human typing speed, etc)
    Qualification questions in knowledgebase file will be answered, scored per incremental question answered. When score reaches threshold, the lead is qualified and contact information emailed.
    Local deployment with Flask and Ngrok
    Add a Whatsapp node for deployment on Whatsapp


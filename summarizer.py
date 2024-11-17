import os
from openai import OpenAI

class OpenAISummarizer:
    def __init__(self, api_key, model="gpt-4o-mini"):
        """
        Initializes the OpenAISummarizer with an API key and model.

        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model to use for summarization.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def summarize(self, text):
        """
        Summarizes the given text using OpenAI's chat completion API.

        Args:
            text (str): The text to summarize.

        Returns:
            str: The summarized text.
        """
        messages = [
            {"role": "system", "content": "going to summarize the wiki article for RAG. Sum it up nicely"},
            {"role": "user", "content": text}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content

    def save_results(self, res_list, dir_name):
        """
        Saves the original and summarized content to files.

        Args:
            res_list (list): A list of tuples containing (title, content).
            dir_name (str): Directory name to save the results.
        """
        os.mkdir(dir_name)
        os.mkdir(f"{dir_name}/output_org")
        os.mkdir(f"{dir_name}/output_summarized")

        for title, content in res_list:
            with open(f"./{dir_name}/output_org/{title}.txt", "w", encoding="utf-8") as f:
                f.write(content)

            summarized_content = self.summarize(content)

            with open(f"./{dir_name}/output_summarized/{title}.txt", "w", encoding="utf-8") as f:
                f.write(summarized_content)

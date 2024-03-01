
<h1 align="center">ChatDoc+</h1>

<p align="center">
  <img src="./imgs/llama_ai.png" alt="">


This repository contains an app that allows users to ask questions about a provided document or engage in a question-answering chatbot conversation. The app is built with Streamlit, Llama-Index, LangChain, Llama-cpp-python, and is powered by the LLM [NeuralBeagle14-7B-GGUF](https://huggingface.co/mlabonne/NeuralBeagle14-7B-GGUF) by Maxime Labonne.

- No OpenAI API key required.
- Runs locally on Macs (Tested on Apple Silicon Mac with macOS Ventura 13.5.1).
- You can turn off your internet connection.

</p>

## Requirements

- Python3.11 or above (should work with Python3.10)
- pip (Python’s package installer)

## Installation

Follow these steps to install and set up the app:

1. **Clone the Repository and Navigate to the Directory**:

   ```bash
   git clone https://github.com/hbacard/chatdoc-plus.git && cd chatdoc-plus
   ```

2. **Create a Python Virtual Environment**:

   ```bash
   python3 -m venv .venv
   ```

3. **Activate the Environment**:
   - On Unix-based systems:

     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   - **Note:** On Linux there might be an error with the installation of `llama-cpp-python`. You can try these steps:
     - `sudo apt-get install build-essential`
     - `pip install -r requirements.txt`

5. **Download the gguf file for `NeuralBeagle14-7B-GGUF`**:

   ```bash
   python3 download_model.py
   ```

6. **Enable GPU with llama-cpp-python**:

   - On Apple Silicon (METAL):

     ```bahs
     CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 pip install --force-reinstall llama-cpp-python==0.1.83 --no-cache-dir
     ```

   - On Linux:

     ```bash
     CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --force-reinstall llama-cpp-python==0.1.83 --no-cache-dir
     ```

7. **Run the App**:

   ```bash
   streamlit run app.py
   ```

Open your browser and navigate to [http://localhost:8501](http://localhost:8501) to interact with the app.

- **Note:** If the app doesn't start you can try these steps:
  - Deactivate the virtual environment with `deactivate`
  - Reactivate it with `source .venv/bin/activate`
  - Then run `streamlit run app.py`

## Usage

The app provides two modes of operation:

1. **Q&A Chat Bot**: When no document is provided, engage in a question-answering conversation with the AI assistant.
2. **Document Query Mode**: Upload a document and ask questions about its content. The AI assistant will process queries using the document as context.

## Contributing

We welcome contributions to improve this app. If you have suggestions or encounter issues, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.

## Notes

you may need to istall poppler to use the library `pdftotext`.
https://stackoverflow.com/questions/45912641/unable-to-install-pdftotext-on-python-3-6-missing-poppler

```bash
brew install poppler
brew install pkg-config poppler python
```

## What is different in this fork respect to the forked repository by Maximilian Winter

In respect to the original ![repo](https://github.com/hbacard/chatdoc-plus) by Maximilian Winter ![this fork](https://github.com/SebastianoX/chatdoc-plus) has very little differences.

- There is a new page to query and scrape ArXiv for getting a series of pdf articles, based on my previously opened source repo ![ScrapXiv](https://github.com/SebastianoF/ScrapXiv).
- There is a new page to scrape huggingface and get more models, other than `neuralbeagle14-7b.Q5_K_M.gguf` by Maxime Labonne.
- The chat is now in a page that allow to select documents from the downloaded papers.
- The python code is packaged and linted.

## Disclaimers

- This is an hobby project and the time for active maintenance will be very limited.
- Please feel free to fork and re-use the code, citing the original repo and the LICENCE.

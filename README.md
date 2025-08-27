# 🤖 AI Chatbot 

A modern, ChatGPT-like chatbot interface built with Streamlit. This application provides a beautiful and responsive chat interface where users can interact with an AI assistant.

## ✨ Features

- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Chat**: Instant message exchange with the AI
- **Message History**: Persistent chat history during the session
- **Timestamps**: Each message shows when it was sent
- **Responsive Design**: Works great on desktop and mobile
- **Clear Chat**: Option to start fresh conversations
- **Loading States**: Visual feedback while AI is processing

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 🎯 Usage

1. **Start a conversation**: Type your message in the input field at the bottom
2. **Send messages**: Click the "Send" button or press Enter
3. **View responses**: The AI will respond with contextual messages
4. **Clear chat**: Use the "Clear Chat" button in the sidebar to start fresh
5. **Chat history**: All messages are preserved during your session

## 🔧 Customization

### Modifying the AI Response Function

The main AI logic is in the `generate_response()` function in `app.py`. You can:

- **Integrate with AI APIs**: Replace the simple response logic with calls to OpenAI, Gemini, or other AI services
- **Add context awareness**: Implement more sophisticated conversation handling
- **Customize responses**: Modify the response patterns and templates

Example with OpenAI integration:
```python
import openai

def generate_response(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content
```

### Styling Customization

The app uses custom CSS for styling. You can modify the appearance by editing the CSS section in the `st.markdown()` call.

## 📁 Project Structure

```
pgagi/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── Untitled.ipynb     # Jupyter notebook (if any)
```

## 🛠️ Technical Details

- **Framework**: Streamlit
- **Styling**: Custom CSS with gradients and animations
- **State Management**: Streamlit session state
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Automatic page refresh on new messages

## 🔮 Future Enhancements

- [ ] Integration with real AI models (OpenAI, Gemini, etc.)
- [ ] File upload and processing
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Conversation export
- [ ] User authentication
- [ ] Database storage for chat history

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Chatting! 🎉** 
import React, { useState } from "react";

const Home = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  const simulateBackendResponse = (userMessage) => {
    setTimeout(() => {
      setMessages((prevMessages) => [...prevMessages, { text: `You said: ${userMessage}`, sender: 'bot' }]);
    }, 1000);
  };

  const handleNewMessageChange = (event) => {
    setNewMessage(event.target.value);
  };

  const handleSendMessage = () => {
    if (newMessage.trim() !== "") {
      setMessages([...messages, { text: newMessage, sender: 'user' }]);
      simulateBackendResponse(newMessage);
      setNewMessage("");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="Main flex flex-col h-screen">
      <div className="flex flex-row items-center justify-between bg-gray-300 h-20 p-4 sticky top-0 z-50">
        <div className="flex flex-row items-center space-x-4">
        <img
            src="/logo.png" 
            alt="logo"
            className="rounded-full h-10"
          />
          <p className="text-black">Green Haven AI</p>
        </div>
        <div className="flex flex-row space-x-4">
          <img
            src="./public/backbtn.svg"
            alt="logo"
            className="rounded-full h-10 fill-black"
          />
          <img
            src="./public/closebtn.svg"
            alt="logo"
            className="rounded-full h-10"
          />
        </div>
      </div>
      <div className="flex flex-col flex-grow overflow-y-auto p-4 space-y-4 bg-white">
        {messages.map((message, index) => (
          <p
            key={index}
            className={`p-2 rounded-lg ${message.sender === 'bot' ? 'bg-gray-200' : 'bg-blue-200'}`}
          >
            {message.text}
          </p>
        ))}
      </div>
      <div className="flex items-center sticky bottom-0 m-5">
        <input
          type="text"
          value={newMessage}
          onChange={handleNewMessageChange}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="flex-grow p-2 rounded-lg border-2 border-gray-400"
        />
        <button onClick={handleSendMessage} className="ml-2 p-2 rounded-lg bg-blue-500 text-white">
          Send
        </button>
      </div>
    </div>
  );
};

export default Home;

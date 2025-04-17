import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      })
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      
      const data = await res.json()
      setResponse(data)
    } catch (error) {
      console.error('Error:', error)
      setResponse({ 
        answer: "Sorry, an error occurred while processing your request.", 
        sources: [] 
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container">
      <h1 className="title">Chromium Android Assistant</h1>

      <form onSubmit={handleSubmit} className="query-form">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="textarea"
          placeholder="Ask about Chromium Android development..."
        />
        <button
          type="submit"
          disabled={isLoading}
          className="button"
        >
          {isLoading ? 'Loading...' : 'Ask Question'}
        </button>
      </form>

      {response && (
        <div className="response-container">
          <h2 className="response-title">Answer:</h2>
          <div className="markdown-content">
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                }
              }}
            >
              {response.answer}
            </ReactMarkdown>
          </div>
          
          {response.sources && response.sources.length > 0 && (
            <>
              <h3 className="sources-title">Sources:</h3>
              <ul className="sources-list">
                {response.sources.map((source, index) => (
                  <li key={index} className="source-item">
                    <code>{source}</code>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default App
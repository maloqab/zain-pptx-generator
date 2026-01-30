import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Loader2, Download, Plus, Wrench, FileText, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'tool'
  content: string
  type?: 'message' | 'tool_call' | 'tool_result'
  tool?: string
  reasoning?: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [slides, setSlides] = useState<any[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  // Start new conversation on mount
  useEffect(() => {
    startNewConversation()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const startNewConversation = async () => {
    try {
      const res = await fetch('http://localhost:5001/api/chat/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      setConversationId(data.conversation_id)
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: data.message
      }])
      setSlides([])
    } catch (err) {
      console.error('Failed to start conversation:', err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !conversationId || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(`http://localhost:5001/api/chat/${conversationId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content })
      })
      const data = await res.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response.content || data.response.reasoning,
        type: data.response.type,
        tool: data.response.tool,
        reasoning: data.response.reasoning
      }

      setMessages(prev => [...prev, assistantMessage])

      // If it's a tool call, execute it automatically
      if (data.response.type === 'tool_call') {
        await executeTool(data.response.tool, data.response.parameters)
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const executeTool = async (toolName: string, parameters: any) => {
    if (!conversationId) return

    try {
      const res = await fetch(`http://localhost:5001/api/chat/${conversationId}/tool`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: toolName, parameters })
      })
      const result = await res.json()

      const toolResultMessage: Message = {
        id: Date.now().toString(),
        role: 'tool',
        content: result.result,
        type: 'tool_result',
        tool: toolName
      }

      setMessages(prev => [...prev, toolResultMessage])

      // Update slides if available
      if (result.slide) {
        setSlides(prev => [...prev, result.slide])
      }

      // If presentation rendered, show download
      if (result.download_url) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: `✅ Presentation ready! Download: http://localhost:5001${result.download_url}`
        }])
      }
    } catch (err) {
      console.error('Tool execution failed:', err)
    }
  }

  const renderPresentation = async () => {
    if (!conversationId || slides.length === 0) return
    
    await executeTool('render_presentation', {
      slides,
      title_gradient: 'ultraviolet',
      section_gradient: 'coraldawn'
    })
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Zain AI Presentation Designer</h1>
              <p className="text-xs text-slate-400">Powered by multi-agent architecture</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={startNewConversation}
              className="border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
            {slides.length > 0 && (
              <Button
                size="sm"
                onClick={renderPresentation}
                className="bg-gradient-to-r from-purple-600 to-pink-600"
              >
                <Download className="w-4 h-4 mr-2" />
                Export ({slides.length} slides)
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="relative z-10 flex-1 container mx-auto px-4 py-6 flex gap-6">
        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <Card className="flex-1 bg-slate-900/50 backdrop-blur-xl border-slate-800 flex flex-col overflow-hidden">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4" ref={scrollRef}>
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <Avatar className={`w-8 h-8 ${
                      message.role === 'user' 
                        ? 'bg-slate-700' 
                        : message.role === 'tool'
                        ? 'bg-green-600'
                        : 'bg-gradient-to-br from-purple-600 to-pink-600'
                    }`}>
                      <AvatarFallback className="text-xs">
                        {message.role === 'user' ? 'You' : message.role === 'tool' ? 'Tool' : 'AI'}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : message.role === 'tool'
                        ? 'bg-green-600/20 border border-green-600/30 text-green-100'
                        : 'bg-slate-800 text-slate-100'
                    }`}>
                      {message.type === 'tool_call' && (
                        <div className="flex items-center gap-2 mb-2 text-sm text-purple-300">
                          <Wrench className="w-4 h-4" />
                          <span>Using tool: {message.tool}</span>
                        </div>
                      )}
                      {message.reasoning && (
                        <div className="text-sm text-slate-400 mb-2 italic">
                          {message.reasoning}
                        </div>
                      )}
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <Avatar className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600">
                      <AvatarFallback className="text-xs">AI</AvatarFallback>
                    </Avatar>
                    <div className="bg-slate-800 rounded-2xl px-4 py-3 flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-slate-400">Thinking...</span>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t border-slate-800">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Describe your presentation or ask for help..."
                  className="flex-1 bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-purple-500"
                />
                <Button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar - Slides & Tools */}
        <div className="w-80 hidden lg:block">
          <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800 h-full">
            <div className="p-4 border-b border-slate-800">
              <h2 className="font-semibold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Slides ({slides.length})
              </h2>
            </div>
            <ScrollArea className="h-[calc(100vh-280px)]">
              <div className="p-4 space-y-2">
                {slides.length === 0 ? (
                  <p className="text-sm text-slate-500 text-center py-8">
                    No slides yet. Start a conversation to create your presentation.
                  </p>
                ) : (
                  slides.map((slide, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-purple-500/50 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-2 h-2 rounded-full ${
                          slide.type === 'title' ? 'bg-purple-500' :
                          slide.type === 'section' ? 'bg-pink-500' : 'bg-slate-500'
                        }`} />
                        <span className="text-xs text-slate-400 capitalize">{slide.type}</span>
                      </div>
                      <p className="text-sm text-slate-200 truncate">{slide.title}</p>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>

            {/* Tools */}
            <div className="p-4 border-t border-slate-800">
              <h3 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Available Tools
              </h3>
              <div className="space-y-2">
                {['create_slide', 'generate_chart', 'analyze_content', 'render_presentation'].map((tool) => (
                  <div key={tool} className="text-xs text-slate-500 flex items-center gap-2">
                    <Wrench className="w-3 h-3" />
                    {tool.replace('_', ' ')}
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

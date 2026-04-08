"use client"

import { useState, useRef, useEffect, FormEvent } from "react"
import { Bot, Paperclip, Mic, CornerDownLeft, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    ChatBubble,
    ChatBubbleAvatar,
    ChatBubbleMessage,
} from "@/components/ui/chat-bubble"
import { ChatInput } from "@/components/ui/chat-input"
import {
    ExpandableChat,
    ExpandableChatHeader,
    ExpandableChatBody,
    ExpandableChatFooter,
} from "@/components/ui/expandable-chat"
import { ChatMessageList } from "@/components/ui/chat-message-list"

const STORAGE_KEY = "medbot_chat_history"

const SYSTEM_PROMPT = `You are MedBot, a helpful AI medical assistant built into the Synapse Medical AI platform.
You help users understand medical concepts, navigate the platform, and answer general health questions.
You are knowledgeable, empathetic, and always remind users to consult real doctors for diagnosis and treatment.
Keep responses concise and friendly. Do not diagnose specific conditions.`

type Message = {
    id: number
    content: string
    sender: "user" | "ai"
}

const INITIAL_MESSAGES: Message[] = [
    { id: 1, content: "Hello! I'm MedBot, your AI medical assistant. How can I help you today?", sender: "ai" },
]

export function ExpandableChatDemo() {
    const [messages, setMessages] = useState<Message[]>(() => {
        if (typeof window === "undefined") return INITIAL_MESSAGES
        try {
            const saved = localStorage.getItem(STORAGE_KEY)
            return saved ? JSON.parse(saved) : INITIAL_MESSAGES
        } catch {
            return INITIAL_MESSAGES
        }
    })

    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const bottomRef = useRef<HTMLDivElement>(null)

    // Persist messages
    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
        } catch {}
    }, [messages])

    // Auto-scroll
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, isLoading])

    const clearHistory = () => {
        setMessages(INITIAL_MESSAGES)
        localStorage.removeItem(STORAGE_KEY)
    }

    const sendMessage = async (userText: string) => {
        const userMsg: Message = { id: Date.now(), content: userText, sender: "user" }
        const updated = [...messages, userMsg]
        setMessages(updated)
        setIsLoading(true)

        try {
            // Build conversation history for context
            const history = updated.map((m) => ({
                role: m.sender === "user" ? "user" : "assistant",
                content: m.content,
            }))

            // Use Hugging Face free inference API with Mistral
            const response = await fetch(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        inputs: buildPrompt(history),
                        parameters: {
                            max_new_tokens: 300,
                            temperature: 0.7,
                            return_full_text: false,
                        },
                    }),
                }
            )

            let aiText = "I'm having trouble connecting right now. Please try again in a moment."

            if (response.ok) {
                const data = await response.json()
                if (Array.isArray(data) && data[0]?.generated_text) {
                    aiText = data[0].generated_text.trim()
                    // Clean up any extra prompting that leaked through
                    aiText = aiText.split("[/INST]").pop()?.trim() || aiText
                    aiText = aiText.replace(/^MedBot:\s*/i, "").trim()
                }
            } else {
                // Fallback: smart rule-based medical responses
                aiText = getMedicalFallback(userText)
            }

            setMessages((prev) => [...prev, { id: Date.now(), content: aiText, sender: "ai" }])
        } catch {
            const fallback = getMedicalFallback(userText)
            setMessages((prev) => [...prev, { id: Date.now(), content: fallback, sender: "ai" }])
        } finally {
            setIsLoading(false)
        }
    }

    function buildPrompt(history: { role: string; content: string }[]) {
        let prompt = `<s>[INST] ${SYSTEM_PROMPT} [/INST]</s>\n`
        for (let i = 0; i < history.length; i++) {
            const m = history[i]
            if (m.role === "user") {
                prompt += `<s>[INST] ${m.content} [/INST]`
            } else {
                prompt += ` ${m.content}</s>\n`
            }
        }
        return prompt
    }

    function getMedicalFallback(text: string): string {
        const lower = text.toLowerCase()
        if (lower.includes("brain") || lower.includes("tumor") || lower.includes("mri"))
            return "For brain MRI analysis, use the NeuroVision module on your dashboard. It can detect glioma, meningioma, and other conditions from MRI scans. Always follow up with a neurologist."
        if (lower.includes("chest") || lower.includes("xray") || lower.includes("lung") || lower.includes("pneumonia"))
            return "For chest X-ray analysis, navigate to the NeuroVision > Chest tab. The AI can screen for conditions like pneumonia, effusion, and more. Please consult a pulmonologist for diagnosis."
        if (lower.includes("bone") || lower.includes("fracture") || lower.includes("orthopedic"))
            return "Bone fracture analysis is available in the NeuroVision module. Upload your X-ray and the AI will help identify potential fractures. Always consult an orthopedic specialist."
        if (lower.includes("appointment") || lower.includes("doctor") || lower.includes("book"))
            return "You can book appointments with specialists directly from the Doctors section in your dashboard. Filter by specialty and choose a convenient time slot."
        if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey"))
            return "Hello! I'm MedBot, your AI medical assistant. I can help you navigate the platform, understand your scan results, or answer general health questions. What can I help you with?"
        if (lower.includes("help") || lower.includes("what can you do"))
            return "I can help you with: 🧠 Brain MRI analysis, 🫁 Chest X-ray interpretation, 🦴 Bone fracture detection, 📅 Booking doctor appointments, and answering general health questions. What would you like to know?"
        return "That's a great question! For accurate medical guidance, I recommend consulting with a qualified healthcare professional. In the meantime, you can use our AI diagnostic tools in the NeuroVision section for initial screening."
    }

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return
        const text = input.trim()
        setInput("")
        sendMessage(text)
    }

    return (
        <div className="h-[300px] relative z-50">
            <ExpandableChat size="sm" position="bottom-right" icon={<Bot className="h-5 w-5" />}>
                <ExpandableChatHeader className="flex-col text-center justify-center">
                    <div className="flex items-center justify-between w-full px-2">
                        <div className="flex-1 text-center">
                            <h1 className="text-lg font-semibold">MedBot AI</h1>
                            <p className="text-xs text-muted-foreground">Medical Assistant</p>
                        </div>
                        <Button variant="ghost" size="icon" onClick={clearHistory} title="Clear chat">
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </ExpandableChatHeader>

                <ExpandableChatBody>
                    <ChatMessageList>
                        {messages.map((message) => (
                            <ChatBubble key={message.id} variant={message.sender === "user" ? "sent" : "received"}>
                                <ChatBubbleAvatar
                                    className="h-5 w-5 shrink-0"
                                    src={
                                        message.sender === "user"
                                            ? "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=64&h=64&q=80&crop=faces&fit=crop"
                                            : "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=64&h=64&q=80&crop=faces&fit=crop"
                                    }
                                    fallback={message.sender === "user" ? "US" : "MB"}
                                />
                                <ChatBubbleMessage variant={message.sender === "user" ? "sent" : "received"}>
                                    {message.content}
                                </ChatBubbleMessage>
                            </ChatBubble>
                        ))}

                        {isLoading && (
                            <ChatBubble variant="received">
                                <ChatBubbleAvatar
                                    className="h-5 w-5 shrink-0"
                                    src="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=64&h=64&q=80&crop=faces&fit=crop"
                                    fallback="MB"
                                />
                                <ChatBubbleMessage isLoading />
                            </ChatBubble>
                        )}
                        <div ref={bottomRef} />
                    </ChatMessageList>
                </ExpandableChatBody>

                <ExpandableChatFooter>
                    <form
                        onSubmit={handleSubmit}
                        className="relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring p-1"
                    >
                        <ChatInput
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault()
                                    handleSubmit(e as unknown as FormEvent)
                                }
                            }}
                            placeholder="Ask MedBot anything..."
                            className="min-h-8 resize-none rounded-lg bg-background border-0 p-2 shadow-none focus-visible:ring-0"
                        />
                        <div className="flex items-center p-2 pt-0 justify-end">
                            <Button type="submit" size="sm" className="ml-auto gap-1" disabled={isLoading}>
                                Send
                                <CornerDownLeft className="size-2.5" />
                            </Button>
                        </div>
                    </form>
                </ExpandableChatFooter>
            </ExpandableChat>
        </div>
    )
}

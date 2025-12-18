import { useState, useEffect } from 'react'
import { Mic, MicOff } from 'lucide-react'

declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

interface VoiceInputProps {
  onTranscript: (text: string) => void
  disabled?: boolean
}

export function VoiceInput({ onTranscript, disabled = false }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.warn("Speech Recognition not supported in this browser")
      return
    }

    const rec = new SpeechRecognition()
    rec.continuous = false
    rec.interimResults = true
    rec.lang = 'en-US'

    rec.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0])
        .map((result: any) => result.transcript)
        .join('')
      if (event.results[event.results.length - 1].isFinal) {
        onTranscript(transcript)
        setIsListening(false)
      }
    }

    rec.onerror = (event: any) => {
      console.error("Speech recognition error", event.error)
      setIsListening(false)
    }

    rec.onend = () => setIsListening(false)

    setRecognition(rec)
  }, [onTranscript])

  const toggleListening = () => {
    if (!recognition || disabled) return

    if (isListening) {
      recognition.stop()
    } else {
      recognition.start()
      setIsListening(true)
    }
  }

  return (
    <button
      onClick={toggleListening}
      disabled={disabled || !recognition}
      className={`px-4 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
        isListening
          ? 'bg-red-500 hover:bg-red-600 text-white'
          : 'bg-slate-700 hover:bg-slate-600 text-white disabled:opacity-50 disabled:cursor-not-allowed'
      }`}
      title={!recognition ? 'Voice input not supported in this browser' : isListening ? 'Click to stop' : 'Click to speak'}
    >
      {isListening ? (
        <>
          <MicOff className="w-5 h-5 animate-pulse" />
          Listening...
        </>
      ) : (
        <>
          <Mic className="w-5 h-5" />
          Speak
        </>
      )}
    </button>
  )
}

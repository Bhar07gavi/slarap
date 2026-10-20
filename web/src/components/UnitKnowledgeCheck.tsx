import React, { useState, useEffect } from 'react'
import {
  HelpCircle,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  BookOpen,
} from 'lucide-react'
import { api } from '../api'

interface Question {
  id: string
  question: string
  options: string[]
}

interface FeedbackItem {
  id: string
  question: string
  chosen_index: number | null
  correct_index: number
  is_correct: boolean
  explanation: string
}

interface UnitKnowledgeCheckProps {
  unitId: string
  unitTitle: string
  onComplete?: () => void
}

export const UnitKnowledgeCheck: React.FC<UnitKnowledgeCheckProps> = ({
  unitId,
  unitTitle,
  onComplete,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState<Record<string, FeedbackItem>>({})
  const [score, setScore] = useState<{ correct: number; total: number } | null>(null)

  const loadQuestions = async () => {
    setLoading(true)
    setSubmitted(false)
    setSelectedAnswers({})
    setFeedback({})
    setScore(null)
    try {
      const data = await api.getQuiz(unitId)
      if (Array.isArray(data)) {
        setQuestions(data)
      } else {
        setQuestions([])
      }
    } catch (err) {
      console.error('Failed to load quiz:', err)
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen && questions.length === 0) {
      loadQuestions()
    }
  }, [isOpen, unitId])

  const handleSelect = (qid: string, optIdx: number) => {
    if (submitted) return
    setSelectedAnswers((prev) => ({ ...prev, [qid]: optIdx }))
  }

  const handleSubmit = async () => {
    if (questions.length === 0) return
    setSubmitting(true)
    try {
      const res = await api.submitQuiz(unitId, selectedAnswers)
      if (res && res.feedback) {
        const fbMap: Record<string, FeedbackItem> = {}
        res.feedback.forEach((item: FeedbackItem) => {
          fbMap[item.id] = item
        })
        setFeedback(fbMap)
        setScore({ correct: res.correct_count, total: res.total_questions })
        setSubmitted(true)

        // Store completion in localStorage
        try {
          localStorage.setItem(`slarap_completed_${unitId}`, 'true')
        } catch {
          // ignore
        }
        if (onComplete) {
          onComplete()
        }
      }
    } catch (err) {
      console.error('Failed to submit quiz:', err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mt-8 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
      {/* Header Toggle */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-800/40 transition"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center text-indigo-400">
            <HelpCircle size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span>Knowledge Check: {unitTitle}</span>
              <span className="text-[10px] font-normal uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                Optional Assessment
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Verify your comprehension of the core OS concepts covered in this lab.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-xs font-medium">{isOpen ? 'Hide Questions' : 'Open Quiz'}</span>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="p-5 border-t border-slate-800 bg-slate-950/40 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-8 text-xs text-slate-400">
              <RefreshCw size={16} className="animate-spin mr-2 text-indigo-400" />
              Loading questions...
            </div>
          ) : questions.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-400">
              No questions found for this unit.
            </div>
          ) : (
            <>
              {/* Score Banner when submitted */}
              {submitted && score && (
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-sm ${
                        score.correct === score.total
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-indigo-950 text-indigo-400 border border-indigo-800'
                      }`}
                    >
                      {Math.round((score.correct / score.total) * 100)}%
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Quiz Evaluation Completed</div>
                      <div className="text-xs text-slate-400">
                        You answered {score.correct} of {score.total} questions correctly.
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={loadQuestions}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
                  >
                    <RefreshCw size={13} />
                    <span>Retake</span>
                  </button>
                </div>
              )}

              {/* Questions List */}
              <div className="space-y-4">
                {questions.map((q, idx) => {
                  const fb = feedback[q.id]
                  const userChoice = selectedAnswers[q.id]

                  return (
                    <div
                      key={q.id}
                      className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 space-y-3"
                    >
                      <div className="flex items-start gap-2.5">
                        <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-mono text-[11px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <div className="text-xs font-semibold text-slate-200 leading-relaxed">
                          {q.question}
                        </div>
                      </div>

                      {/* Options Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-7">
                        {q.options.map((opt, optIdx) => {
                          const isSelected = userChoice === optIdx
                          let style =
                            'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'

                          if (submitted && fb) {
                            if (fb.correct_index === optIdx) {
                              style =
                                'bg-emerald-950/50 border-emerald-500/80 text-emerald-200 font-medium'
                            } else if (isSelected && !fb.is_correct) {
                              style = 'bg-rose-950/50 border-rose-500/80 text-rose-200'
                            } else {
                              style = 'bg-slate-950/40 border-slate-900 text-slate-400'
                            }
                          } else if (isSelected) {
                            style = 'bg-indigo-950/60 border-indigo-500 text-indigo-200 font-medium'
                          }

                          return (
                            <button
                              key={optIdx}
                              disabled={submitted}
                              onClick={() => handleSelect(q.id, optIdx)}
                              className={`p-3 rounded-lg border text-left text-xs transition flex items-center justify-between gap-2 ${style}`}
                            >
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-slate-400 uppercase text-[10px]">
                                  {String.fromCharCode(65 + optIdx)}.
                                </span>
                                <span>{opt}</span>
                              </div>
                              {submitted && fb && fb.correct_index === optIdx && (
                                <CheckCircle2 size={15} className="text-emerald-400 flex-shrink-0" />
                              )}
                              {submitted && fb && isSelected && !fb.is_correct && (
                                <XCircle size={15} className="text-rose-400 flex-shrink-0" />
                              )}
                            </button>
                          )
                        })}
                      </div>

                      {/* Explanation */}
                      {submitted && fb && (
                        <div className="mt-2 pl-7 text-[11px] text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/60">
                          <span className="font-semibold text-slate-300">Explanation: </span>
                          {fb.explanation}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>

              {/* Submit Button */}
              {!submitted && (
                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-slate-400">
                    {Object.keys(selectedAnswers).length} of {questions.length} answered
                  </span>
                  <button
                    onClick={handleSubmit}
                    disabled={submitting || Object.keys(selectedAnswers).length === 0}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg text-xs font-semibold transition"
                  >
                    {submitting ? 'Evaluating...' : 'Submit Answers'}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

import { useState, useCallback } from 'react'
import './App.css'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Loader2, Download, Sparkles, FileText, RefreshCw } from 'lucide-react'

const gradients = [
  { value: 'ultraviolet', label: 'Ultraviolet', colors: 'from-[#6E2C91] to-[#9B59B6]' },
  { value: 'coraldawn', label: 'Coral Dawn', colors: 'from-[#E6007E] to-[#F5A623]' },
  { value: 'limelagoon', label: 'Lime Lagoon', colors: 'from-[#00A9CE] to-[#7ED321]' },
  { value: 'midnightsky', label: 'Midnight', colors: 'from-[#1A1A1A] to-[#4A4A4A]' },
]

function App() {
  const [outline, setOutline] = useState('')
  const [titleGradient, setTitleGradient] = useState('ultraviolet')
  const [sectionGradient, setSectionGradient] = useState('coraldawn')
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<{filename: string; slideCount: number; downloadUrl: string} | null>(null)
  const [error, setError] = useState('')

  const handleGenerate = useCallback(async () => {
    if (!outline.trim()) {
      setError('Please enter an outline')
      return
    }
    
    setIsGenerating(true)
    setError('')
    
    try {
      const formData = new FormData()
      formData.append('outline', outline)
      formData.append('title_gradient', titleGradient)
      formData.append('section_gradient', sectionGradient)
      
      const response = await fetch('http://localhost:8080/generate', {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (data.success) {
        setResult({
          filename: data.filename,
          slideCount: data.slide_count,
          downloadUrl: data.download_url
        })
      } else {
        setError(data.error || 'Generation failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }, [outline, titleGradient, sectionGradient])

  const handleReset = () => {
    setOutline('')
    setResult(null)
    setError('')
  }

  const loadExample = () => {
    setOutline(`# Q4 2025 Strategy Review
Driving Growth Through Digital Innovation

## Market Performance

- Revenue increased 15% year-over-year to $1.2B
- Customer base expanded by 2.4M subscribers
- 5G coverage now reaches 85% of population
- Market share grew from 16% to 18%

## Financial Highlights

- Operating profit: $450M (up 12% YoY)
- EBITDA margin improved to 42%
- Free cash flow: $280M

## Looking Ahead to 2026

- Expand 5G to rural and remote areas
- Launch super-app for digital services
- Enter fintech with Zain Pay`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Animated background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-600/30 to-pink-600/30 border border-purple-500/30 mb-6">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-200">AI-Powered</span>
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
            Zain PPTX Generator
          </h1>
          <p className="text-slate-400 text-lg">
            Create professional presentations with intelligent design
          </p>
        </div>

        {result ? (
          // Result View
          <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
            <CardContent className="p-12 text-center">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-green-400 to-cyan-400 flex items-center justify-center">
                <Download className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-2">Your Presentation is Ready!</h2>
              <p className="text-slate-400 mb-8">
                {result.slideCount} intelligently designed slides
              </p>
              <div className="flex gap-4 justify-center">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  onClick={() => window.open(`http://localhost:8080${result.downloadUrl}`, '_blank')}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download PPTX
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={handleReset}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Create Another
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          // Form View
          <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
            <CardContent className="p-8 space-y-8">
              {/* Outline Input */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                  Presentation Outline
                </Label>
                <Textarea
                  value={outline}
                  onChange={(e) => setOutline(e.target.value)}
                  placeholder="# Presentation Title&#10;Subtitle goes here&#10;&#10;## Section Title&#10;&#10;- Bullet point one&#10;- Bullet point two&#10;- Bullet point three"
                  className="min-h-[250px] bg-slate-950/50 border-slate-700 text-slate-200 placeholder:text-slate-600 resize-none"
                />
              </div>

              {/* Title Gradient Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                  Title Slide Style
                </Label>
                <RadioGroup
                  value={titleGradient}
                  onValueChange={setTitleGradient}
                  className="grid grid-cols-2 md:grid-cols-4 gap-4"
                >
                  {gradients.map((g) => (
                    <div key={g.value}>
                      <RadioGroupItem
                        value={g.value}
                        id={`title-${g.value}`}
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor={`title-${g.value}`}
                        className="flex flex-col items-center gap-2 cursor-pointer"
                      >
                        <div className={`w-full h-16 rounded-lg bg-gradient-to-r ${g.colors} ring-2 ring-transparent peer-data-[state=checked]:ring-white transition-all`} />
                        <span className="text-xs text-slate-400">{g.label}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              {/* Section Gradient Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                  Section Divider Style
                </Label>
                <RadioGroup
                  value={sectionGradient}
                  onValueChange={setSectionGradient}
                  className="grid grid-cols-2 md:grid-cols-4 gap-4"
                >
                  {gradients.map((g) => (
                    <div key={g.value}>
                      <RadioGroupItem
                        value={g.value}
                        id={`section-${g.value}`}
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor={`section-${g.value}`}
                        className="flex flex-col items-center gap-2 cursor-pointer"
                      >
                        <div className={`w-full h-16 rounded-lg bg-gradient-to-r ${g.colors} ring-2 ring-transparent peer-data-[state=checked]:ring-white transition-all`} />
                        <span className="text-xs text-slate-400">{g.label}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              {error && (
                <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                  {error}
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Button
                  size="lg"
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate with AI
                    </>
                  )}
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={loadExample}
                  disabled={isGenerating}
                  className="border-slate-700 text-slate-300 hover:bg-slate-800"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Try Example
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-slate-500 text-sm">
          Zain Brand Compliant • AI-Powered Design • Professional Templates
        </div>
      </div>
    </div>
  )
}

export default App

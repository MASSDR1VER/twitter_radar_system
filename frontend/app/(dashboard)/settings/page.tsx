"use client"

import { useState, useEffect } from "react"
import { Twitter, CheckCircle, AlertCircle, Upload } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Textarea } from "@/components/ui/textarea"

export default function SettingsPage() {
  // Twitter Account State
  const [twitterAccount, setTwitterAccount] = useState<any>(null)
  const [cookieJson, setCookieJson] = useState("")
  const [twitterLoading, setTwitterLoading] = useState(false)
  const [twitterMessage, setTwitterMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  // API Keys State
  const [selectedProvider, setSelectedProvider] = useState<"openai" | "anthropic" | null>(null)
  const [apiKey, setApiKey] = useState("")
  const [apiKeysStatus, setApiKeysStatus] = useState<any>(null)
  const [apiKeyLoading, setApiKeyLoading] = useState(false)
  const [apiKeyMessage, setApiKeyMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  useEffect(() => {
    fetchTwitterAccount()
    fetchAPIKeysStatus()
  }, [])

  const fetchTwitterAccount = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/settings/twitter/account")
      const data = await response.json()
      if (data.authenticated) {
        setTwitterAccount(data.user)
      }
    } catch (error) {
      console.error("Failed to fetch Twitter account:", error)
    }
  }

  const fetchAPIKeysStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/settings/api-keys/status")
      const data = await response.json()
      setApiKeysStatus(data)
    } catch (error) {
      console.error("Failed to fetch API keys status:", error)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setCookieJson(content)
      }
      reader.readAsText(file)
    }
  }

  const handleTwitterValidation = async () => {
    setTwitterLoading(true)
    setTwitterMessage(null)

    try {
      // Parse JSON
      const cookies = JSON.parse(cookieJson)

      // Send directly to backend - it will handle both formats
      const response = await fetch("http://localhost:8000/api/v1/settings/twitter/validate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(cookies)
      })

      const data = await response.json()

      if (response.ok) {
        setTwitterMessage({ type: "success", text: data.message })
        setTwitterAccount(data.user)
        setCookieJson("")
      } else {
        setTwitterMessage({ type: "error", text: data.detail || "Failed to validate cookies" })
      }
    } catch (error: any) {
      setTwitterMessage({ type: "error", text: error.message || "Invalid JSON format" })
    } finally {
      setTwitterLoading(false)
    }
  }

  const handleSaveAPIKey = async () => {
    if (!selectedProvider) return

    setApiKeyLoading(true)
    setApiKeyMessage(null)

    try {
      const payload: any = {}
      if (selectedProvider === "openai") {
        payload.openai_api_key = apiKey
      } else if (selectedProvider === "anthropic") {
        payload.anthropic_api_key = apiKey
      }

      const response = await fetch("http://localhost:8000/api/v1/settings/api-keys", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (response.ok) {
        setApiKeyMessage({ type: "success", text: data.message })
        setApiKey("")
        setSelectedProvider(null)
        fetchAPIKeysStatus()
      } else {
        setApiKeyMessage({ type: "error", text: data.detail || "Failed to save API key" })
      }
    } catch (error) {
      setApiKeyMessage({ type: "error", text: "Failed to connect to server" })
    } finally {
      setApiKeyLoading(false)
    }
  }

  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Configure your Twitter account and AI providers
        </p>
      </div>

      {/* Twitter Account Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Twitter className="h-5 w-5" />
            Twitter Account
          </CardTitle>
          <CardDescription>
            Upload cookie.json file to authenticate
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Account */}
          {twitterAccount && (
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 border rounded-lg bg-muted/50">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={twitterAccount.avatar_url} />
                  <AvatarFallback>{twitterAccount.username?.[0]?.toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{twitterAccount.name}</h3>
                    {twitterAccount.verified && (
                      <CheckCircle className="h-4 w-4 text-blue-500" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">@{twitterAccount.username}</p>
                  <div className="flex gap-4 mt-2 text-sm">
                    <span><strong>{twitterAccount.followers_count?.toLocaleString()}</strong> Followers</span>
                    <span><strong>{twitterAccount.following_count?.toLocaleString()}</strong> Following</span>
                  </div>
                </div>
              </div>
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Twitter account is connected and authenticated
                </AlertDescription>
              </Alert>
            </div>
          )}

          {/* Cookie JSON Upload */}
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Upload cookie.json</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Create a JSON file with your Twitter cookies:
              </p>
              <div className="bg-muted p-4 rounded-lg font-mono text-xs mb-4">
                {`{
  "ct0": "your_ct0_cookie",
  "auth_token": "your_auth_token",
  "kdt": "your_kdt_cookie"
}`}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cookie-file">Upload cookie.json file</Label>
              <Input
                id="cookie-file"
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="cursor-pointer"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cookie-json">Or paste JSON directly</Label>
              <Textarea
                id="cookie-json"
                placeholder='{"ct0": "...", "auth_token": "...", "kdt": "..."}'
                value={cookieJson}
                onChange={(e) => setCookieJson(e.target.value)}
                rows={6}
                className="font-mono text-xs"
              />
            </div>

            {twitterMessage && (
              <Alert variant={twitterMessage.type === "error" ? "destructive" : "default"}>
                {twitterMessage.type === "success" ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>{twitterMessage.text}</AlertDescription>
              </Alert>
            )}

            <Button
              onClick={handleTwitterValidation}
              disabled={twitterLoading || !cookieJson}
            >
              {twitterLoading ? "Validating..." : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Validate & Save
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* API Keys Section */}
      <Card>
        <CardHeader>
          <CardTitle>AI Provider API Keys</CardTitle>
          <CardDescription>
            Configure API keys for your chosen AI provider
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Status */}
          {apiKeysStatus && (
            <div className="grid gap-4 md:grid-cols-2">
              <Card className={apiKeysStatus.openai?.configured ? "border-green-500" : ""}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">OpenAI (GPT-4)</CardTitle>
                </CardHeader>
                <CardContent>
                  {apiKeysStatus.openai?.configured ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm font-medium">Configured</span>
                      </div>
                      <p className="text-xs text-muted-foreground font-mono">
                        {apiKeysStatus.openai.key_preview}
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedProvider("openai")
                          setApiKey("")
                        }}
                      >
                        Update Key
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">Not configured</span>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedProvider("openai")
                          setApiKey("")
                        }}
                      >
                        Add Key
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className={apiKeysStatus.anthropic?.configured ? "border-green-500" : ""}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Anthropic (Claude)</CardTitle>
                </CardHeader>
                <CardContent>
                  {apiKeysStatus.anthropic?.configured ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm font-medium">Configured</span>
                      </div>
                      <p className="text-xs text-muted-foreground font-mono">
                        {apiKeysStatus.anthropic.key_preview}
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedProvider("anthropic")
                          setApiKey("")
                        }}
                      >
                        Update Key
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">Not configured</span>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedProvider("anthropic")
                          setApiKey("")
                        }}
                      >
                        Add Key
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* API Key Input (Dynamic based on selected provider) */}
          {selectedProvider && (
            <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold">
                  {selectedProvider === "openai" ? "OpenAI" : "Anthropic"} API Key
                </h4>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedProvider(null)
                    setApiKey("")
                  }}
                >
                  Cancel
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="api-key">
                  {selectedProvider === "openai" ? "OpenAI API Key" : "Anthropic API Key"}
                </Label>
                <Input
                  id="api-key"
                  type="password"
                  placeholder={selectedProvider === "openai" ? "sk-..." : "sk-ant-..."}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Get your key from{" "}
                  <a
                    href={selectedProvider === "openai"
                      ? "https://platform.openai.com/api-keys"
                      : "https://console.anthropic.com/"}
                    target="_blank"
                    className="underline"
                  >
                    {selectedProvider === "openai" ? "OpenAI Platform" : "Anthropic Console"}
                  </a>
                </p>
              </div>

              {apiKeyMessage && (
                <Alert variant={apiKeyMessage.type === "error" ? "destructive" : "default"}>
                  {apiKeyMessage.type === "success" ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <AlertCircle className="h-4 w-4" />
                  )}
                  <AlertDescription>{apiKeyMessage.text}</AlertDescription>
                </Alert>
              )}

              <Button
                onClick={handleSaveAPIKey}
                disabled={apiKeyLoading || !apiKey}
              >
                {apiKeyLoading ? "Saving..." : "Save API Key"}
              </Button>
            </div>
          )}

          {!selectedProvider && (
            <p className="text-sm text-muted-foreground text-center py-4">
              Click "Add Key" or "Update Key" above to configure an API key
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

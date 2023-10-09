export type Step = {
  id: string
  label: React.ReactNode
  onClick?: (e: React.MouseEvent) => void
  url?: string
  hash?: string
}

export interface StepPattern {
  id: string
  label: string
  path?: string
  isActive: boolean
}

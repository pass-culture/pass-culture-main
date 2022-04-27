export type Step = {
  id: string
  label: string
  onClick?: (e: React.MouseEvent) => void
  url?: string
  hash?: string
}

export interface IStepPattern {
  id: string
  label: string
  path?: string
  isActive: boolean
}

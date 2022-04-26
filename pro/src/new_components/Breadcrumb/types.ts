export type Step = {
  id: string
  label: string
  onClick?: (e: React.MouseEvent) => void
  url?: string
  hash?: string
}

export type TStepList = { [key: string]: Step }

export interface IStepPattern {
  id: string
  label: string
  path: string
  url?: string
}

export type TStepPatternList = { [key: string]: IStepPattern }

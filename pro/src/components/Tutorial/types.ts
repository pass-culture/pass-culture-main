export interface StepComponentProps {
  titleId: string
  contentClassName: string
}

export interface Step {
  position: number
  component: React.ComponentType<StepComponentProps>
  className: string
}

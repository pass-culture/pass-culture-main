export interface IStepComponentProps {
  titleId: string
  contentClassName: string
}

export interface IStep {
  position: number
  component: React.ComponentType<IStepComponentProps>
}

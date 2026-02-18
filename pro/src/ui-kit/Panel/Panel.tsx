import style from './Panel.module.scss'

export interface PanelProps {
  children?: React.ReactNode | React.ReactNode[]
}

export const Panel = ({ children }: PanelProps): JSX.Element => (
  <div className={style['panel']}>{children}</div>
)

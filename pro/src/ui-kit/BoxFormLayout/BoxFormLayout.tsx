import style from './BoxFormLayout.module.scss'
import { Header } from './components/BoxFormLayoutHeader'

export interface BoxFormLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
}

export const BoxFormLayout = ({
  children,
}: BoxFormLayoutProps): JSX.Element => (
  <div className={style['box-form-layout']}>{children}</div>
)

BoxFormLayout.Header = Header

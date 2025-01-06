import cn from 'classnames'

import style from './BoxFormLayout.module.scss'
import { Banner } from './components/BoxFormLayoutBanner'
import { Fields } from './components/BoxFormLayoutFields'
import { FormHeader } from './components/BoxFormLayoutFormHeader'
import { Header } from './components/BoxFormLayoutHeader'
import { RequiredMessage } from './components/BoxFormLayoutRequiredMessage'

export interface BoxFormLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
}

export const BoxFormLayout = ({
  children,
  className,
}: BoxFormLayoutProps): JSX.Element => (
  <div className={cn(style['box-form-layout'], className)}>{children}</div>
)

BoxFormLayout.Header = Header
BoxFormLayout.Banner = Banner
BoxFormLayout.Fields = Fields
BoxFormLayout.FormHeader = FormHeader
BoxFormLayout.RequiredMessage = RequiredMessage

import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'
import Fields from './BoxFormLayoutFields'
import Header from './BoxFormLayoutHeader'

interface IBoxFormLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
}

const BoxFormLayout = ({
  children,
  className,
}: IBoxFormLayoutProps): JSX.Element => (
  <div className={cn(style['box-form-layout'], className)}>{children}</div>
)

BoxFormLayout.Header = Header
BoxFormLayout.Fields = Fields

export default BoxFormLayout

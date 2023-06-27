import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'
import Banner from './BoxFormLayoutBanner'
import Fields from './BoxFormLayoutFields'
import FormHeader from './BoxFormLayoutFormHeader'
import Header from './BoxFormLayoutHeader'
import RequiredMessage from './BoxFormLayoutRequiredMessage'

interface BoxFormLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
}

const BoxFormLayout = ({
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

export default BoxFormLayout

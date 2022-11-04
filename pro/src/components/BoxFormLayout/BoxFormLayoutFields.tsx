import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutFields {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
}

const Fields = ({ className, children }: BoxFormLayoutFields): JSX.Element => (
  <div className={cn(style['box-form-layout-fields'], className)}>
    {children}
  </div>
)

export default Fields

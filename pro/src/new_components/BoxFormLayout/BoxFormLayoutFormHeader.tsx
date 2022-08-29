import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutFormHeaderProps {
  className?: string
  textPrimary: string
  textSecondary: string
}

const FormHeader = ({
  className,
  textPrimary,
  textSecondary,
}: BoxFormLayoutFormHeaderProps): JSX.Element => (
  <div className={cn(style['box-form-layout-form-header'], className)}>
    <span className={style['box-form-layout-form-header-secondary']}>
      {textSecondary}
    </span>
    {' : '}
    <span>{textPrimary}</span>
  </div>
)

export default FormHeader

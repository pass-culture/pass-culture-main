import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSubSectionProps {
  title: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

export const SubSection = ({
  title,
  children,
  className,
  description,
}: FormLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-sub-section'], className)}>
    <h3 className={style['form-layout-sub-section-title']}>{title}</h3>

    {description && (
      <div className={style['form-layout-section-header']}>
        <FormLayoutDescription description={description} />
      </div>
    )}
    {children}
  </div>
)

import cn from 'classnames'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import React from 'react'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSubSectionProps {
  title: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  isNew?: boolean
}

export const SubSection = ({
  title,
  children,
  className,
  description,
  isNew,
}: FormLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-sub-section'], className)}>
    <div className={style['form-layout-sub-section-title-wrapper']}>
      <h3 className={style['form-layout-sub-section-title']}>{title}</h3>
      {isNew && <Tag label="Nouveau" variant={TagVariant.NEW} />}
    </div>

    {description && (
      <div className={style['form-layout-section-header']}>
        <FormLayoutDescription description={description} />
      </div>
    )}
    {children}
  </div>
)

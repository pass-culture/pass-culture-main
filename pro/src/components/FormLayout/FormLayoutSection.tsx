import cn from 'classnames'
import React from 'react'

import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSectionProps {
  title?: React.ReactNode
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  id?: string
  isNew?: boolean
}

export const Section = ({
  title,
  description,
  children,
  className,
  id,
  isNew,
}: FormLayoutSectionProps): JSX.Element => {
  return (
    <fieldset className={cn(style['form-layout-section'], className)} id={id}>
      {isNew ? (
        <div className={style['new-tag']}>
          {title && (
            <legend>
              <h2 className={style['form-layout-section-title']}>{title}</h2>
            </legend>
          )}
          {<Tag variant={TagVariant.BLUE}>Nouveau</Tag>}
        </div>
      ) : (
        title && (
          <legend>
            <h2 className={style['form-layout-section-title']}>{title}</h2>
          </legend>
        )
      )}

      <div className={style['form-layout-section-header']}>
        <FormLayoutDescription description={description} />
      </div>
      {children}
    </fieldset>
  )
}

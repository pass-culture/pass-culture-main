import cn from 'classnames'
import type React from 'react'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSectionProps {
  title?: React.ReactNode
  accessibleLabel?: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  id?: string
}

export const Section = ({
  title,
  accessibleLabel,
  description,
  children,
  className,
  id,
}: FormLayoutSectionProps): JSX.Element => {
  return (
    <fieldset className={cn(style['form-layout-section'], className)} id={id}>
      {(title || accessibleLabel) && (
        <legend
          className={cn({
            [style['form-layout-section-legend--spaced']]:
              title && !description,
            [style['form-layout-section-legend--visually-hidden']]: !title,
          })}
        >
          {title ? (
            <h2 className={style['form-layout-section-title']}>{title}</h2>
          ) : (
            accessibleLabel
          )}
        </legend>
      )}
      {description && (
        <div className={style['form-layout-section-header']}>
          <FormLayoutDescription description={description} />
        </div>
      )}
      {children}
    </fieldset>
  )
}

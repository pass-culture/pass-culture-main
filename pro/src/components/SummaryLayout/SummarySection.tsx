import cn from 'classnames'
import React, { ReactNode } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  editLink?: string | ReactNode
  'aria-label'?: string
}

export const SummarySection = ({
  title,
  children,
  className,
  editLink,
  ...props
}: SummaryLayoutSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-section'], className)}>
    <div className={style['summary-layout-section-header']}>
      <h2 className={style['section-title']}>{title}</h2>

      {typeof editLink === 'string' ? (
        <ButtonLink
          to={editLink}
          aria-label={props['aria-label']}
          className={style['summary-layout-section-header-edit-link']}
          icon={fullEditIcon}
        >
          Modifier
        </ButtonLink>
      ) : (
        editLink
      )}
    </div>
    {children}
  </div>
)

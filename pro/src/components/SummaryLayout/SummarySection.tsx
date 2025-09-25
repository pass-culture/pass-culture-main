import cn from 'classnames'
import type React from 'react'
import type { JSX, ReactNode } from 'react'

import fullEditIcon from '@/icons/full-edit.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { Divider } from '@/ui-kit/Divider/Divider'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  editLink?: string | ReactNode
  'aria-label'?: string
  shouldShowDivider?: boolean
}

export const SummarySection = ({
  title,
  children,
  className,
  editLink,
  shouldShowDivider = false,
  ...props
}: SummaryLayoutSectionProps): JSX.Element => (
  <div
    className={cn(
      style['summary-layout-section'],
      {
        [style['summary-layout-section-with-divider']]: shouldShowDivider,
      },
      className
    )}
  >
    <div className={style['summary-layout-section-header']}>
      <h2
        className={cn(style['section-title'], {
          [style['section-title-editable']]: Boolean(editLink),
        })}
      >
        {title}
      </h2>

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
    {shouldShowDivider && <Divider size="large" />}
  </div>
)

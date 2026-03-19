import cn from 'classnames'
import type React from 'react'

import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import { Divider } from '@/ui-kit/Divider/Divider'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  shouldShowDivider?: boolean
  isNew?: boolean
}

export const SummarySubSection = ({
  title,
  children,
  className,
  shouldShowDivider = true,
  isNew,
}: SummaryLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-sub-section'], className)}>
    <div className={style['summary-layout-sub-section-title-wrapper']}>
      <h3 className={style['summary-layout-sub-section-title']}>{title}</h3>
      {isNew && <Tag label="Nouveau" variant={TagVariant.NEW} />}
    </div>
    {children}
    {shouldShowDivider && <Divider size="large" />}
  </div>
)

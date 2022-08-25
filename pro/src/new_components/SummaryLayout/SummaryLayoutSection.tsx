import cn from 'classnames'
import React from 'react'

import { ReactComponent as BlackPen } from 'icons/ico-pen-black.svg'
import { ButtonLink, Title } from 'ui-kit'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  editLink: string
  onLinkClick?: () => void
}

const Section = ({
  title,
  children,
  className,
  editLink,
  onLinkClick,
}: ISummaryLayoutSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-section'], className)}>
    <div className={style['summary-layout-section-header']}>
      <div className={style['summary-layout-section-header-content']}>
        <Title as="h3" level={3}>
          {title}
        </Title>
        <ButtonLink
          link={{ to: editLink, isExternal: false }}
          className={style['summary-layout-section-header-edit-link']}
          Icon={BlackPen}
          onClick={onLinkClick ? onLinkClick : undefined}
        >
          Modifier
        </ButtonLink>
      </div>
      <div className={style['summary-layout-section-header-separator']}></div>
    </div>
    {children}
  </div>
)

export default Section

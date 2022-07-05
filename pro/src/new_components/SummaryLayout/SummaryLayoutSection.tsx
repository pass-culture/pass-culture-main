import { ButtonLink, Title } from 'ui-kit'

import { ReactComponent as BlackPen } from 'icons/ico-pen-black.svg'
import React from 'react'
import cn from 'classnames'
import style from './SummaryLayout.module.scss'

interface ISummaryLayoutSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  editLink: string
}

const Section = ({
  title,
  children,
  className,
  editLink,
}: ISummaryLayoutSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-section'], className)}>
    <div className={style['summary-layout-section-header']}>
      <div className={style['summary-layout-section-header-content']}>
        <Title as="h3" level={3}>
          {title}
        </Title>
        <ButtonLink
          to={editLink}
          className={style['summary-layout-section-header-edit-link']}
          Icon={BlackPen}
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

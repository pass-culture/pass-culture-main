import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

import style from './FormLayout.module.scss'

interface IFormLayoutSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const SubSection = ({
  title,
  children,
  className,
}: IFormLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-sub-section'], className)}>
    <Title as="h3" className={style['form-layout-sub-section-title']} level={4}>
      {title}
    </Title>
    {children}
  </div>
)

export default SubSection

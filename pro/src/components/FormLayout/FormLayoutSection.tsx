import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

import style from './FormLayout.module.scss'

interface IFormLayoutSectionProps {
  title: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const Section = ({
  title,
  description,
  children,
  className,
}: IFormLayoutSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-section'], className)}>
    <div className={style['form-layout-section-header']}>
      <Title as="h2" level={3}>
        {title}
      </Title>
      {description && (
        <p className={style['form-layout-section-description']}>
          {description}
        </p>
      )}
    </div>
    {children}
  </div>
)

export default Section

import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSubSectionProps {
  title: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const SubSection = ({
  title,
  children,
  className,
  description,
}: FormLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-sub-section'], className)}>
    <Title as="h3" className={style['form-layout-sub-section-title']} level={4}>
      {title}
    </Title>
    {description && (
      <div className={style['form-layout-section-header']}>
        <FormLayoutDescription description={description} />
      </div>
    )}
    {children}
  </div>
)

export default SubSection

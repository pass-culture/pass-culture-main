import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

import style from './FormLayout.module.scss'
import { FormLayoutDescription } from './FormLayoutDescription'

interface FormLayoutSectionProps {
  title: React.ReactNode
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  id?: string
}

const Section = ({
  title,
  description,
  children,
  className,
  id,
}: FormLayoutSectionProps): JSX.Element => (
  <fieldset className={cn(style['form-layout-section'], className)} id={id}>
    <legend>
      <Title as="h2" level={3}>
        {title}
      </Title>
    </legend>
    <div className={style['form-layout-section-header']}>
      <FormLayoutDescription description={description} />
    </div>
    {children}
  </fieldset>
)

export default Section

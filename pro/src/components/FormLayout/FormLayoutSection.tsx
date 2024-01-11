import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'
import { Link } from 'ui-kit/Banners/LinkNodes/LinkNodes'

import style from './FormLayout.module.scss'

import { FormLayoutDescription } from '.'

interface FormLayoutSectionProps {
  title: React.ReactNode
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  descriptionAsBanner?: boolean
  links?: Link[]
  id?: string
}

const Section = ({
  title,
  description,
  children,
  className,
  descriptionAsBanner = false,
  links,
  id,
}: FormLayoutSectionProps): JSX.Element => (
  <fieldset className={cn(style['form-layout-section'], className)} id={id}>
    <legend>
      <Title as="h2" level={3}>
        {title}
      </Title>
    </legend>
    <div className={style['form-layout-section-header']}>
      <FormLayoutDescription
        description={description}
        isBanner={descriptionAsBanner}
        links={links}
      />
    </div>
    {children}
  </fieldset>
)

export default Section

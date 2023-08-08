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
  <fieldset>
    <div className={cn(style['form-layout-section'], className)} id={id}>
      <div className={style['form-layout-section-header']}>
        <legend>
          <Title as="h2" level={3}>
            {title}
          </Title>
        </legend>
        <FormLayoutDescription
          description={description}
          isBanner={descriptionAsBanner}
          links={links}
        />
      </div>
      {children}
    </div>
  </fieldset>
)

export default Section

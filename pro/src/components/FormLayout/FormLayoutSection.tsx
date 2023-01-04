import cn from 'classnames'
import React from 'react'

import { Title, Banner } from 'ui-kit'
import { Link } from 'ui-kit/Banners/Banner'

import style from './FormLayout.module.scss'

interface IFormLayoutSectionProps {
  title: string
  description?: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  descriptionAsBanner?: boolean
  links?: Link[]
}

const Section = ({
  title,
  description,
  children,
  className,
  descriptionAsBanner = false,
  links,
}: IFormLayoutSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-section'], className)}>
    <div className={style['form-layout-section-header']}>
      <Title as="h2" level={3}>
        {title}
      </Title>
      {description && !descriptionAsBanner && (
        <p className={style['form-layout-section-description']}>
          {description}
        </p>
      )}
      {description && descriptionAsBanner && (
        <Banner
          type="notification-info"
          className={style['form-layout-section-description']}
          links={links}
        >
          {description}
        </Banner>
      )}
    </div>
    {children}
  </div>
)

export default Section

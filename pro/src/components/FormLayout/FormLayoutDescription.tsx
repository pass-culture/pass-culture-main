import React from 'react'

import { Banner } from 'ui-kit'
import { Link } from 'ui-kit/Banners/Banner'

import style from './FormLayout.module.scss'

interface IFormLayoutDescriptionProps {
  description?: string
  className?: string
  isBanner?: boolean
  links?: Link[]
}
const Description = ({
  description,
  isBanner = false,
  links,
}: IFormLayoutDescriptionProps): JSX.Element => (
  <>
    {description && !isBanner && (
      <p className={style['form-layout-section-description-content']}>
        {description}
      </p>
    )}
    {description && isBanner && (
      <div className={style['form-layout-section-description-container']}>
        <Banner
          type="notification-info"
          className={style['form-layout-section-description-content']}
          links={links}
        >
          {description}
        </Banner>
      </div>
    )}
  </>
)

export default Description

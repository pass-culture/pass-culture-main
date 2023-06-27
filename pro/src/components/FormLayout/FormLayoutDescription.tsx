import React from 'react'

import { Banner } from 'ui-kit'
import { Link } from 'ui-kit/Banners/Banner'

import style from './FormLayout.module.scss'

export interface FormLayoutDescriptionProps {
  description?: string
  isBanner?: boolean
  links?: Link[]
}
const Description = ({
  description,
  isBanner = false,
  links,
}: FormLayoutDescriptionProps): JSX.Element => (
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

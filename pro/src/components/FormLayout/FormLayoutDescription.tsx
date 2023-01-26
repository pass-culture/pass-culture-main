import React from 'react'

import { Banner } from 'ui-kit'
import { Link } from 'ui-kit/Banners/Banner'

import style from './FormLayout.module.scss'

interface IFormLayoutSectionProps {
  description?: string
  className?: string
  isBanner?: boolean
  links?: Link[]
}
const FormLayoutDescription = ({
  description,
  isBanner = false,
  links,
}: IFormLayoutSectionProps): JSX.Element => (
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

export default FormLayoutDescription

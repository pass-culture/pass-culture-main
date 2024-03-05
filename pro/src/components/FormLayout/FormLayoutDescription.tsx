import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { Link } from 'ui-kit/Banners/LinkNodes/LinkNodes'

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
        <Callout
          variant={CalloutVariant.DEFAULT}
          className={style['form-layout-section-description-content']}
          links={links}
        >
          {description}
        </Callout>
      </div>
    )}
  </>
)

export default Description

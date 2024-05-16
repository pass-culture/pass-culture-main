import cn from 'classnames'
import React from 'react'

import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { Link } from 'ui-kit/Banners/LinkNodes/LinkNodes'

import style from './FormLayout.module.scss'

export interface FormLayoutDescriptionProps {
  description?: string | JSX.Element
  isBanner?: boolean
  links?: Link[]
  className?: string
}

export const FormLayoutDescription = ({
  description,
  isBanner = false,
  links,
  className,
}: FormLayoutDescriptionProps): JSX.Element => (
  <>
    {description && !isBanner && (
      <p className={style['form-layout-section-description-content']}>
        {description}
      </p>
    )}
    {description && isBanner && (
      <div
        className={cn(
          style['form-layout-section-description-container'],
          className
        )}
      >
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

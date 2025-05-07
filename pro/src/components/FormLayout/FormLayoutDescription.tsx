import cn from 'classnames'

import { Callout } from 'ui-kit/Callout/Callout'
import { Link } from 'ui-kit/LinkNodes/LinkNodes'

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
          className={style['form-layout-section-description-content']}
          links={links}
        >
          {description}
        </Callout>
      </div>
    )}
  </>
)

import type { Link } from '@/ui-kit/LinkNodes/LinkNodes'

import style from './FormLayout.module.scss'

export interface FormLayoutDescriptionProps {
  description?: string | JSX.Element
  links?: Link[]
  className?: string
}

export const FormLayoutDescription = ({
  description,
}: FormLayoutDescriptionProps): JSX.Element => (
  <>
    {description && (
      <p className={style['form-layout-section-description-content']}>
        {description}
      </p>
    )}
  </>
)

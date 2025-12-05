import style from './FormLayout.module.scss'

export interface FormLayoutDescriptionProps {
  description?: string | JSX.Element
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

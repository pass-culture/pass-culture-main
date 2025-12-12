import cn from 'classnames'

import style from './FormLayout.module.scss'

interface FormLayoutMandatoryInfoProps {
  className?: string
  areAllFieldsMandatory?: boolean
}

export const MandatoryInfo = ({
  className,
  areAllFieldsMandatory = false,
}: FormLayoutMandatoryInfoProps): JSX.Element => {
  return (
    <p className={cn(style['mandatory-info'], className)}>
      {areAllFieldsMandatory
        ? 'Tous les champs sont obligatoires.'
        : 'Les champs suivis d’un * sont obligatoires.'}
    </p>
  )
}

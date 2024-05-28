import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface FormLayoutMandatoryInfoProps {
  className?: string
}

export const MandatoryInfo = ({
  className,
}: FormLayoutMandatoryInfoProps): JSX.Element => {
  return (
    <p className={cn(style['mandatory-info'], className)}>
      Tous les champs suivis d’un * sont obligatoires.
    </p>
  )
}

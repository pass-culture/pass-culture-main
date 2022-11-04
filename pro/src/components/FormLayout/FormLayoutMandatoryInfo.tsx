import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface IFormLayoutMandatoryInfoProps {
  className?: string
}

const MandatoryInfo = ({
  className,
}: IFormLayoutMandatoryInfoProps): JSX.Element => {
  return (
    <p className={cn(style['mandatory-info'], className)}>
      Tous les champs sont obligatoires sauf mention contraire.
    </p>
  )
}

export default MandatoryInfo

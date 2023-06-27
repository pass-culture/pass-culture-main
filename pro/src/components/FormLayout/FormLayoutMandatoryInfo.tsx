import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface FormLayoutMandatoryInfoProps {
  className?: string
}

const MandatoryInfo = ({
  className,
}: FormLayoutMandatoryInfoProps): JSX.Element => {
  return (
    <p className={cn(style['mandatory-info'], className)}>
      Tous les champs sont obligatoires sauf mention contraire.
    </p>
  )
}

export default MandatoryInfo

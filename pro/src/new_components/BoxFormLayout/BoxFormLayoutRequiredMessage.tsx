import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutRequiredMessageProps {
  className?: string
}

const RequiredMessage = ({
  className,
}: BoxFormLayoutRequiredMessageProps): JSX.Element => (
  <div className={cn(style['box-form-layout-required-message'], className)}>
    Tous les champs sont obligatoires sauf mention contraire.
  </div>
)

export default RequiredMessage

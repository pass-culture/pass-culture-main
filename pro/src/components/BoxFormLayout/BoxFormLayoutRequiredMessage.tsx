import cn from 'classnames'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutRequiredMessageProps {
  className?: string
}

export const RequiredMessage = ({
  className,
}: BoxFormLayoutRequiredMessageProps): JSX.Element => (
  <FormLayout.MandatoryInfo
    className={cn(style['box-form-layout-required-message'], className)}
  />
)

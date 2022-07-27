import cn from 'classnames'
import React from 'react'

import style from './OfferFormLayout.module.scss'

interface IOfferFormLayoutStepperProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutStepper = ({
  children,
  className,
}: IOfferFormLayoutStepperProps): JSX.Element => (
  <div className={cn(style['stepper'], className)}>{children}</div>
)

export default OfferFormLayoutStepper

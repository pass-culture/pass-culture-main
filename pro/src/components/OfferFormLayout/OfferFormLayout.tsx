import React from 'react'

import Content from './OfferFormLayoutContent'
import Stepper from './OfferFormLayoutStepper'
import TitleBlock from './OfferFormLayoutTitleBlock'

interface OfferFormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayout = ({
  children,
  className,
}: OfferFormLayoutProps): JSX.Element => (
  <div className={className}>{children}</div>
)

OfferFormLayout.TitleBlock = TitleBlock
OfferFormLayout.Stepper = Stepper
OfferFormLayout.Content = Content

export default OfferFormLayout

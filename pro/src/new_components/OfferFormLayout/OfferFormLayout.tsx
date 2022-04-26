import cn from 'classnames'
import React from 'react'

import style from './OfferFormLayout.module.scss'
import ActionBar from './OfferFormLayoutActionBar'
import Content from './OfferFormLayoutContent'
import Stepper from './OfferFormLayoutStepper'
import TitleBlock from './OfferFormLayoutTitleBlock'

interface IOfferFormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayout = ({
  children,
  className,
}: IOfferFormLayoutProps): JSX.Element => (
  <div className={cn(style['form-layout'], className)}>{children}</div>
)

OfferFormLayout.TitleBlock = TitleBlock
OfferFormLayout.Stepper = Stepper
OfferFormLayout.Content = Content
OfferFormLayout.ActionBar = ActionBar

export default OfferFormLayout

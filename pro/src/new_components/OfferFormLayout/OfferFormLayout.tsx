import ActionBar from './OfferFormLayoutActionBar'
import Content from './OfferFormLayoutContent'
import React from 'react'
import Stepper from './OfferFormLayoutStepper'
import TitleBlock from './OfferFormLayoutTitleBlock'
import cn from 'classnames'
import style from './OfferFormLayout.module.scss'

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

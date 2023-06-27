import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import Actions from './FormLayoutActions'
import MandatoryInfo from './FormLayoutMandatoryInfo'
import Row from './FormLayoutRow'
import RowWithInfo from './FormLayoutRowWithInfo'
import Section from './FormLayoutSection'
import SubSection from './FormLayoutSubSection'

interface FormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  small?: boolean
  fullWidthActions?: boolean
}

const FormLayout = ({
  children,
  className,
  small = false,
  fullWidthActions = false,
}: FormLayoutProps): JSX.Element => (
  <div
    className={cn(
      style['form-layout'],
      { [style.small]: small },
      { [style['full-width-actions']]: fullWidthActions },
      className
    )}
  >
    {children}
  </div>
)

FormLayout.RowWithInfo = RowWithInfo
FormLayout.Row = Row
FormLayout.SubSection = SubSection
FormLayout.Section = Section
FormLayout.Actions = Actions
FormLayout.MandatoryInfo = MandatoryInfo

export default FormLayout

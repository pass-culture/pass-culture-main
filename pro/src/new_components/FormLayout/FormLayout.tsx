import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import Actions from './FormLayoutActions'
import Row from './FormLayoutRow'
import RowWithInfo from './FormLayoutRowWithInfo'
import Section from './FormLayoutSection'
import SubSection from './FormLayoutSubSection'

interface IFormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  small?: boolean
}

const FormLayout = ({
  children,
  className,
  small,
}: IFormLayoutProps): JSX.Element => (
  <div
    className={cn(style['form-layout'], { [style.small]: small }, className)}
  >
    {children}
  </div>
)

FormLayout.RowWithInfo = RowWithInfo
FormLayout.Row = Row
FormLayout.SubSection = SubSection
FormLayout.Section = Section
FormLayout.Actions = Actions

export default FormLayout

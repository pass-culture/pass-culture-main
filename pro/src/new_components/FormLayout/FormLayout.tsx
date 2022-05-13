import Actions from './FormLayoutActions'
import React from 'react'
import Row from './FormLayoutRow'
import Section from './FormLayoutSection'
import SubSection from './FormLayoutSubSection'
import cn from 'classnames'
import style from './FormLayout.module.scss'

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

FormLayout.Row = Row
FormLayout.SubSection = SubSection
FormLayout.Section = Section
FormLayout.Actions = Actions

export default FormLayout

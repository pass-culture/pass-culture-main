import cn from 'classnames'

import style from './FormLayout.module.scss'
import { Actions } from './FormLayoutActions'
import { MandatoryInfo } from './FormLayoutMandatoryInfo'
import { Row } from './FormLayoutRow'
import { RowWithInfo } from './FormLayoutRowWithInfo'
import { Section } from './FormLayoutSection'
import { SubSection } from './FormLayoutSubSection'

export interface FormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  fullWidthActions?: boolean
}

export const FormLayout = ({
  children,
  className,
  fullWidthActions = false,
}: FormLayoutProps): JSX.Element => (
  <div
    className={cn(
      style['form-layout'],
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

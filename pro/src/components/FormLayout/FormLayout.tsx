import cn from 'classnames'

import style from './FormLayout.module.scss'
import { Actions } from './FormLayoutActions'
import { MandatoryInfo } from './FormLayoutMandatoryInfo'
import { Row } from './FormLayoutRow'
import { RowWithInfo } from './FormLayoutRowWithInfo'
import { Section } from './FormLayoutSection'
import { SubSection } from './FormLayoutSubSection'
import { SubSubSection } from './FormLayoutSubSubSection'
export interface FormLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  fullWidthActions?: boolean
  mediumWidthActions?: boolean
  mediumWidthForm?: boolean
}

export const FormLayout = ({
  children,
  className,
  fullWidthActions = false,
  mediumWidthActions = false,
  mediumWidthForm = false,
}: FormLayoutProps): JSX.Element => (
  <div
    className={cn(
      style['form-layout'],
      { [style['full-width-actions']]: fullWidthActions },
      { [style['medium-width-actions']]: mediumWidthActions },
      { [style['medium-width-form']]: mediumWidthForm },
      className
    )}
  >
    {children}
  </div>
)

FormLayout.RowWithInfo = RowWithInfo
FormLayout.Row = Row
FormLayout.SubSubSection = SubSubSection
FormLayout.SubSection = SubSection
FormLayout.Section = Section
FormLayout.Actions = Actions
FormLayout.MandatoryInfo = MandatoryInfo

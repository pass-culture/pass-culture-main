import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'
import Content from './SummaryLayoutContent'
import Row from './SummaryLayoutRow'
import Section from './SummaryLayoutSection'
import Side from './SummaryLayoutSide'
import SubSection from './SummaryLayoutSubSection'

interface ISummaryLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
}

const SummaryLayout = ({
  children,
  className,
}: ISummaryLayoutProps): JSX.Element => (
  <div className={cn(style['summary-layout'], className)}>{children}</div>
)

SummaryLayout.Content = Content
SummaryLayout.Side = Side
SummaryLayout.Row = Row
SummaryLayout.SubSection = SubSection
SummaryLayout.Section = Section

export default SummaryLayout

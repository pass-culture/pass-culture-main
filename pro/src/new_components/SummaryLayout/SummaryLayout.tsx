import React from 'react'
import Row from './SummaryLayoutRow'
import Section from './SummaryLayoutSection'
import SubSection from './SummaryLayoutSubSection'
import cn from 'classnames'
import style from './SummaryLayout.module.scss'

interface ISummaryLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const SummaryLayout = ({
  children,
  className,
}: ISummaryLayoutProps): JSX.Element => (
  <div className={cn(style['summary-layout'], className)}>{children}</div>
)

SummaryLayout.Row = Row
SummaryLayout.SubSection = SubSection
SummaryLayout.Section = Section

export default SummaryLayout

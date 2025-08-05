import cn from 'classnames'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSubSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

export const SummarySubSubSection = ({
  title,
  children,
  className,
}: SummaryLayoutSubSubSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-sub-sub-section'], className)}>
    <h4 className={style['summary-layout-sub-sub-section-title']}>{title}</h4>
    {children}
  </div>
)

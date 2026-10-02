import cn from 'classnames'

import style from './FormLayout.module.scss'
import styles from './FormLayoutSubSubSection.module.scss'

interface FormLayoutSubSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

export const SubSubSection = ({
  title,
  children,
  className,
}: FormLayoutSubSubSectionProps): JSX.Element => (
  <div className={cn(style['form-layout-sub-sub-section'], className)}>
    <h4 className={styles['subsection-title']}>{title}</h4>
    {children}
  </div>
)

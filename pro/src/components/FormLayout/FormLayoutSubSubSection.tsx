import cn from 'classnames'

import { Title } from '@/ui-kit/Title/Title'

import style from './FormLayout.module.scss'

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
    <Title level="4" title={title} marginBottom="l" />
    {children}
  </div>
)

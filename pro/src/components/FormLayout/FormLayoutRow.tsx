import cn from 'classnames'
import type React from 'react'

import style from './FormLayout.module.scss'
import { RowWithInfo } from './FormLayoutRowWithInfo'

interface FormLayoutRowProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  lgSpaceAfter?: boolean
  mdSpaceAfter?: boolean
  smSpaceAfter?: boolean
  sideComponent?: JSX.Element | null
  testId?: string
}

export const Row = ({
  children,
  className,
  inline,
  lgSpaceAfter,
  mdSpaceAfter,
  smSpaceAfter,
  sideComponent,
  testId,
}: FormLayoutRowProps): JSX.Element => {
  return sideComponent !== undefined ? (
    <RowWithInfo
      className={className}
      inline={inline}
      lgSpaceAfter={lgSpaceAfter}
      mdSpaceAfter={mdSpaceAfter}
      smSpaceAfter={smSpaceAfter}
      sideComponent={sideComponent}
      testId={testId}
    >
      {children}
    </RowWithInfo>
  ) : (
    <div
      className={cn(style['form-layout-row'], className, {
        [style['inline-group']]: inline,
        [style['large-space-after']]: lgSpaceAfter,
        [style['medium-space-after']]: mdSpaceAfter,
        [style['small-space-after']]: smSpaceAfter,
      })}
      data-testid={testId}
    >
      {children}
    </div>
  )
}

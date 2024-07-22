import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import { RowWithInfo } from './FormLayoutRowWithInfo'

interface FormLayoutRowProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  mdSpaceAfter?: boolean
  smSpaceAfter?: boolean
  sideComponent?: JSX.Element | null
}

export const Row = ({
  children,
  className,
  inline,
  mdSpaceAfter,
  smSpaceAfter,
  sideComponent,
}: FormLayoutRowProps): JSX.Element => {
  return sideComponent !== undefined ? (
    <RowWithInfo
      className={className}
      inline={inline}
      mdSpaceAfter={mdSpaceAfter}
      smSpaceAfter={smSpaceAfter}
      sideComponent={sideComponent}
    >
      {children}
    </RowWithInfo>
  ) : (
    <div
      className={cn(style['form-layout-row'], className, {
        [style['inline-group'] ?? '']: inline,
        [style['medium-space-after'] ?? '']: mdSpaceAfter,
        [style['small-space-after'] ?? '']: smSpaceAfter,
      })}
    >
      {children}
    </div>
  )
}

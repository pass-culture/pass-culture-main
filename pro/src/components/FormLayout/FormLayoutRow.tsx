import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import RowWithInfo from './FormLayoutRowWithInfo'

interface IFormLayoutRowProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  lgSpaceAfter?: boolean
  smSpaceAfter?: boolean
  sideComponent?: JSX.Element | null
}

const Row = ({
  children,
  className,
  inline,
  lgSpaceAfter,
  smSpaceAfter,
  sideComponent,
}: IFormLayoutRowProps): JSX.Element => {
  return sideComponent !== undefined ? (
    <RowWithInfo
      className={className}
      inline={inline}
      lgSpaceAfter={lgSpaceAfter}
      smSpaceAfter={smSpaceAfter}
      sideComponent={sideComponent}
    >
      {children}
    </RowWithInfo>
  ) : (
    <div
      className={cn(style['form-layout-row'], className, {
        [style['inline-group']]: inline,
        [style['large-space-after']]: lgSpaceAfter,
        [style['small-space-after']]: smSpaceAfter,
      })}
    >
      {children}
    </div>
  )
}

export default Row

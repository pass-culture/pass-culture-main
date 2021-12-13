import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface IFormLayoutRowProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  lgSpaceAfter?: boolean
}

const Row = ({
  children,
  className,
  inline,
  lgSpaceAfter,
}: IFormLayoutRowProps): JSX.Element => (
  <div
    className={cn(style['form-layout-row'], className, {
      [style['inline-group']]: inline,
      [style['large-space-after']]: lgSpaceAfter,
    })}
  >
    {children}
  </div>
)

export default Row

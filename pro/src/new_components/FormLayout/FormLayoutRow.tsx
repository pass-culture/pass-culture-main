import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface IFormLayoutRowProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
}

const Row = ({
  children,
  className,
  inline,
}: IFormLayoutRowProps): JSX.Element => (
  <div
    className={cn(style['form-layout-row'], className, {
      [style['inline-group']]: inline,
    })}
  >
    {children}
  </div>
)

export default Row

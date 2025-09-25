import cn from 'classnames'
import React, { type JSX } from 'react'

import style from './FormLayout.module.scss'

interface FormLayoutActionsProps {
  children: React.ReactElement<any>[] | React.ReactElement<any>
  className?: string
}

const addActionClass = (
  element: React.ReactElement<any>,
  index?: number
): JSX.Element =>
  React.cloneElement(element, {
    ...element.props,
    key: index,
    className: cn(style['form-layout-action'], element.props.className),
  })

export const Actions = ({
  children,
  className,
}: FormLayoutActionsProps): JSX.Element => (
  <div className={cn(style['form-layout-actions'], className)}>
    {Array.isArray(children)
      ? children.map(addActionClass)
      : addActionClass(children)}
  </div>
)

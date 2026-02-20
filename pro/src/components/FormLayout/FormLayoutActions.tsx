import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

type ActionElement = React.ReactElement<{ className?: string }>

interface FormLayoutActionsProps {
  children: ActionElement[] | ActionElement
  className?: string
}

const addActionClass = (element: ActionElement, index?: number): JSX.Element =>
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

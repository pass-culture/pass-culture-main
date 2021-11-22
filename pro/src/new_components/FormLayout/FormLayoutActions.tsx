import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'

interface IFormLayoutActionsProps {
  children: React.ReactElement[]
  className?: string
}

const Actions = ({
  children,
  className,
}: IFormLayoutActionsProps): JSX.Element => (
  <div className={cn(style['form-layout-actions'], className)}>
    {children.map(Action =>
      React.cloneElement(Action, {
        ...Action.props,
        className: cn(style['form-layout-action'], Action.props.className),
      })
    )}
  </div>
)

export default Actions

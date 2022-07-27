import cn from 'classnames'
import React from 'react'

import styles from './FieldGroup.module.scss'

interface IFieldGroupProps {
  children: React.ReactElement[]
  className?: string
}

const addFieldGroupItemClass = (
  element: React.ReactElement,
  index?: number
): JSX.Element =>
  React.cloneElement(element, {
    ...element.props,
    key: index,
    className: cn(styles['field-group-item'], element.props.className),
  })

const FieldGroup = ({ children, className }: IFieldGroupProps): JSX.Element => (
  <div className={cn(styles['field-group'], className)}>
    {children.map(addFieldGroupItemClass)}
  </div>
)

export default FieldGroup

import cn from 'classnames'
import type { LocationDescriptor } from 'history'
import React from 'react'
import { NavLink } from 'react-router-dom'

import Icon from 'ui-kit/Icon/Icon'

import styles from './GoBackLink.module.scss'

interface GoBackLinkProps {
  to: LocationDescriptor
  title: string
  className?: string
}

const GoBackLink = ({ to, title, className }: GoBackLinkProps): JSX.Element => (
  <NavLink className={cn(styles['go-back-button'], className)} to={to}>
    <Icon svg="ico-circle-arrow" className={styles['go-back-icon']} />
    {title}
  </NavLink>
)

export default GoBackLink

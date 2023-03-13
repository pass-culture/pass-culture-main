import cn from 'classnames'
import React from 'react'
import { NavLink } from 'react-router-dom'

import Icon from 'ui-kit/Icon/Icon'

import styles from './GoBackLink.module.scss'

interface GoBackLinkProps {
  to:
    | {
        pathname?: string
        state?: { scrollToElementId: string }
      }
    | string
  title: string
  className?: string
}

const GoBackLink = ({ to, title, className }: GoBackLinkProps): JSX.Element => (
  <NavLink className={cn(styles['go-back-button'], className)} to={to}>
    <Icon svg="ico-circle-arrow-left" className={styles['go-back-icon']} />
    {title}
  </NavLink>
)

export default GoBackLink

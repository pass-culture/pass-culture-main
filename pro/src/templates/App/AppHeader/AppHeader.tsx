import cn from 'classnames'
import React from 'react'

import styles from './AppHeader.module.scss'

interface IAppHeaderProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const AppHeader = ({ children, className }: IAppHeaderProps): JSX.Element => {
  return <div className={cn(styles['app-header'], className)}>{children}</div>
}

export default AppHeader

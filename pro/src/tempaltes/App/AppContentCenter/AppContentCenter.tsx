import cn from 'classnames'
import React from 'react'

import styles from './AppContentCenter.module.scss'

interface IAppContentCenterProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const AppContentCenter = ({
  children,
  className,
}: IAppContentCenterProps): JSX.Element => {
  return (
    <div className={cn(styles['app-content-center'], className)}>
      {children}
    </div>
  )
}

export default AppContentCenter

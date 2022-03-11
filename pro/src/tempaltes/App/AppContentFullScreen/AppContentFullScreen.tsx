import cn from 'classnames'
import React from 'react'

import styles from './AppContentFullScreen.module.scss'

interface IAppHeaderProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const AppContentFullScreen = ({
  children,
  className,
}: IAppHeaderProps): JSX.Element => {
  return (
    <div className={cn(styles['app-content-fullscreen'], className)}>
      {children}
    </div>
  )
}

export default AppContentFullScreen

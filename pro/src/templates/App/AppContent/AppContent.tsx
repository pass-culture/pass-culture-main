import cn from 'classnames'
import React from 'react'

import styles from './AppContent.module.scss'

interface IAppContentProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const AppContent = ({
  children,
  className,
}: IAppContentProps): JSX.Element => {
  return (
    <div className={cn(styles['app-content'], className)}>
      {children}
    </div>
  )
}

export default AppContent

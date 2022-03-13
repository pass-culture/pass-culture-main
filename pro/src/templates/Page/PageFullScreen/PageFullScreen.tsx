import cn from 'classnames'
import React from 'react'

import styles from './PageFullScreen.module.scss'

interface IPageFullScreenProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const PageFullScreen = ({
  children,
  className,
}: IPageFullScreenProps): JSX.Element => {
  return (
    <div className={cn(styles['page-fullscreen'], className)}>
      {children}
    </div>
  )
}

export default PageFullScreen

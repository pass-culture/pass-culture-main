import cn from 'classnames'
import React from 'react'

import styles from './PageCenter.module.scss'

interface IPageCenterProps {
  className?: string
  children: React.ReactElement[] | React.ReactElement
}

const PageCenter = ({
  children,
  className,
}: IPageCenterProps): JSX.Element => {
  return (
    <div className={cn(styles['page-center'], className)}>
      {children}
    </div>
  )
}

export default PageCenter

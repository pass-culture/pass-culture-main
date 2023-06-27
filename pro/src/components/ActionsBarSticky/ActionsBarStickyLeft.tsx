import React from 'react'

import style from './ActionsBarSticky.module.scss'

interface ActionsBarStickyLeftProps {
  children: React.ReactNode
}

const Left = ({ children }: ActionsBarStickyLeftProps): JSX.Element | null => {
  return children ? <div className={style['left']}>{children}</div> : null
}

export default Left

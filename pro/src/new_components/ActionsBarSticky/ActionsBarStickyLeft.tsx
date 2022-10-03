import React from 'react'

import style from './ActionsBarSticky.module.scss'

interface IActionsBarStickyLeftProps {
  children: React.ReactNode
}

const Left = ({ children }: IActionsBarStickyLeftProps): JSX.Element | null => {
  return children ? <div className={style['left']}>{children}</div> : null
}

export default Left

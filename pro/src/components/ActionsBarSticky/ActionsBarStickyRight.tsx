import React from 'react'

import style from './ActionsBarSticky.module.scss'

export interface IActionsBarStickyRightProps {
  children: React.ReactNode
}

const Right = ({
  children,
}: IActionsBarStickyRightProps): JSX.Element | null => {
  return children ? <div className={style['right']}>{children}</div> : null
}

export default Right

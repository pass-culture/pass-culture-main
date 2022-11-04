import classnames from 'classnames'
import React from 'react'

import style from './ActionsBarSticky.module.scss'
import Left from './ActionsBarStickyLeft'
import Right from './ActionsBarStickyRight'

export interface IActionsBarStickyProps {
  children: React.ReactNode
}

const ActionsBarSticky = ({
  children,
}: IActionsBarStickyProps): JSX.Element => {
  return (
    <div className={classnames(style['actions-bar'])} data-testid="actions-bar">
      <div className={style['actions-bar-content']}>{children}</div>
    </div>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

export default ActionsBarSticky

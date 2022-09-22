import classnames from 'classnames'
import React from 'react'

import style from './ActionsBarSticky.module.scss'

export interface IActionsBarStickyProps {
  isVisible?: boolean
  left?: JSX.Element
  right?: JSX.Element
}

const ActionsBarSticky = ({
  isVisible = false,
  left,
  right,
}: IActionsBarStickyProps): JSX.Element => {
  if (!isVisible) return <></>

  return (
    <div className={classnames(style['actions-bar'])} data-testid="actions-bar">
      <div className={style['actions-bar-content']}>
        <div className={style['left']}>{left}</div>
        {right && <div className={style['right']}>{right}</div>}
      </div>
    </div>
  )
}

export default ActionsBarSticky

import classnames from 'classnames'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'

import { setIsStickyBarOpen } from 'store/reducers/notificationReducer'

import style from './ActionsBarSticky.module.scss'
import Left from './ActionsBarStickyLeft'
import Right from './ActionsBarStickyRight'

export interface IActionsBarStickyProps {
  children: React.ReactNode
}

const ActionsBarSticky = ({
  children,
}: IActionsBarStickyProps): JSX.Element => {
  const dispatch = useDispatch()
  useEffect(() => {
    dispatch(setIsStickyBarOpen(true))
    return () => {
      dispatch(setIsStickyBarOpen(false))
    }
  }, [])
  return (
    <div className={classnames(style['actions-bar'])} data-testid="actions-bar">
      <div className={style['actions-bar-content']}>{children}</div>
    </div>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

export default ActionsBarSticky

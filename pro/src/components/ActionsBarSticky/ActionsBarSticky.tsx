import classnames from 'classnames'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'

import { setIsStickyBarOpen } from 'store/reducers/notificationReducer'

import style from './ActionsBarSticky.module.scss'
import Left from './ActionsBarStickyLeft'
import Right from './ActionsBarStickyRight'

interface ActionsBarStickyProps {
  children: React.ReactNode
  className?: string
}

const ActionsBarSticky = ({
  children,
  className,
}: ActionsBarStickyProps): JSX.Element => {
  const dispatch = useDispatch()
  useEffect(() => {
    dispatch(setIsStickyBarOpen(true))
    return () => {
      dispatch(setIsStickyBarOpen(false))
    }
  }, [])
  return (
    <div
      className={classnames(style['actions-bar'], className)}
      data-testid="actions-bar"
    >
      <div className={style['actions-bar-content']}>{children}</div>
    </div>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

export default ActionsBarSticky

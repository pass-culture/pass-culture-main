import classnames from 'classnames'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'

import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import { setIsStickyBarOpen } from 'store/notifications/reducer'

import style from './ActionsBarSticky.module.scss'
import { Left } from './ActionsBarStickyLeft'
import { Right } from './ActionsBarStickyRight'

interface ActionsBarStickyProps {
  children: React.ReactNode
  className?: string
  hasSideNav?: boolean
}

export const ActionsBarSticky = ({
  children,
  className,
  hasSideNav = true,
}: ActionsBarStickyProps): JSX.Element => {
  const dispatch = useDispatch()
  useEffect(() => {
    dispatch(setIsStickyBarOpen(true))
    return () => {
      dispatch(setIsStickyBarOpen(false))
    }
  }, [dispatch])

  const isNewInterfaceActive = useIsNewInterfaceActive()

  return (
    <div
      className={classnames(
        style['actions-bar'],
        {
          [style['actions-bar-new-interface']]:
            isNewInterfaceActive && hasSideNav,
        },
        className
      )}
      data-testid="actions-bar"
    >
      <div
        className={classnames(style['actions-bar-content'], {
          [style['actions-bar-content-new-interface']]:
            isNewInterfaceActive && hasSideNav,
        })}
      >
        {children}
      </div>
    </div>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

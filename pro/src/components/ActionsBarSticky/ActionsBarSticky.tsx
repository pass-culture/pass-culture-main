import classnames from 'classnames'
import { setIsStickyBarOpen } from 'commons/store/notifications/reducer'
import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

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

  return (
    <div
      className={classnames(
        style['actions-bar'],
        {
          [style['actions-bar-new-interface']]: hasSideNav,
        },
        className
      )}
      data-testid="actions-bar"
    >
      <div
        className={classnames(style['actions-bar-content'], {
          [style['actions-bar-content-new-interface']]: hasSideNav,
        })}
      >
        {children}
      </div>
    </div>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

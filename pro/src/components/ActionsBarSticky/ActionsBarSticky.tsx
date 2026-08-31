import classnames from 'classnames'
import { useEffect, useRef } from 'react'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useIsElementVisible } from '@/commons/hooks/useIsElementVisible'
import { setIsStickyBarOpen } from '@/commons/store/snackBar/reducer'

import style from './ActionsBarSticky.module.scss'
import { Left } from './ActionsBarStickyLeft'
import { Right } from './ActionsBarStickyRight'

interface ActionsBarStickyProps {
  children: React.ReactNode
  className?: string
  hasSideNav?: boolean
  // Floating bar that follows scroll and docks at the bottom of a table,
  // instead of staying fixed at the bottom of the page.
  isEmbedded?: boolean
}

export const ActionsBarSticky = ({
  children,
  className,
  hasSideNav = true,
  isEmbedded = false,
}: ActionsBarStickyProps): JSX.Element => {
  const dispatch = useAppDispatch()
  const embeddedEndSentinelRef = useRef<HTMLDivElement>(null)
  const [isEmbeddedEndSentinelVisible] = useIsElementVisible(
    embeddedEndSentinelRef
  )
  const isEmbeddedEndReached = isEmbedded && isEmbeddedEndSentinelVisible

  useEffect(() => {
    dispatch(setIsStickyBarOpen(true))
    return () => {
      dispatch(setIsStickyBarOpen(false))
    }
  }, [dispatch])

  return (
    <>
      <div
        className={classnames(
          style['actions-bar'],
          {
            [style['actions-bar-new-interface']]: hasSideNav,
            [style['actions-bar-embedded']]: isEmbedded,
            [style['actions-bar-embedded-flat']]: isEmbeddedEndReached,
            [style['actions-bar-embedded-separator']]: isEmbeddedEndReached,
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
      <div
        ref={embeddedEndSentinelRef}
        className={style['actions-bar-embedded-sentinel']}
        aria-hidden="true"
      />
    </>
  )
}

ActionsBarSticky.Left = Left
ActionsBarSticky.Right = Right

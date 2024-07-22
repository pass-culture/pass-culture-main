import cn from 'classnames'

import style from './ActionsBarSticky.module.scss'

interface ActionsBarStickyRightProps {
  children: React.ReactNode
  inverseWhenSmallerThanTablet?: boolean
}

export const Right = ({
  children,
  inverseWhenSmallerThanTablet = false,
}: ActionsBarStickyRightProps): JSX.Element | null => {
  return children ? (
    <div
      className={cn(style['right'], {
        [style['right-inverse'] ?? '']: inverseWhenSmallerThanTablet,
      })}
    >
      {children}
    </div>
  ) : null
}

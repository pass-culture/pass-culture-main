import React from 'react'

import style from './ActionsBarSticky.module.scss'

interface ActionsBarStickyRightProps {
  children: React.ReactNode
}

const Right = ({
  children,
}: ActionsBarStickyRightProps): JSX.Element | null => {
  return children ? <div className={style['right']}>{children}</div> : null
}

export default Right

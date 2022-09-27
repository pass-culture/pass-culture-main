import React, { useState } from 'react'

import styles from './TooltipWrapper.module.scss'

export interface ITooltipWrapperProps {
  delay?: number
  title: string
  children: React.ReactNode | React.ReactNode[]
}

const TooltipWrapper = ({
  delay = 200,
  title,
  children,
}: ITooltipWrapperProps) => {
  const [showTooltip, setShowTooltip] = useState(false)
  let timeout: NodeJS.Timeout | undefined

  const showTip = () => {
    timeout = setTimeout(() => setShowTooltip(true), delay)
  }

  const hideTip = () => {
    clearTimeout(timeout)
    setShowTooltip(false)
  }

  return (
    <div
      onMouseEnter={showTip}
      onMouseLeave={hideTip}
      className={styles['tooltip-wrapper']}
    >
      {showTooltip && (
        <div className={styles['tooltip-wrapper-title']}>{title}</div>
      )}
      {children}
    </div>
  )
}

export default TooltipWrapper

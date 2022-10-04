import React, { useEffect, useState } from 'react'

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
  const [height, setHeight] = useState(0)

  let timeout: NodeJS.Timeout | undefined
  const tooltipId = `tooltip-wrapper-title-${title}`

  const showTip = () => {
    timeout = setTimeout(() => setShowTooltip(true), delay)
  }

  const hideTip = () => {
    clearTimeout(timeout)
    setShowTooltip(false)
  }

  useEffect(() => {
    const refheight = document.getElementById(tooltipId)?.offsetHeight
    setHeight(refheight ?? 0)
  }, [])

  return (
    <div
      onMouseEnter={showTip}
      onMouseLeave={hideTip}
      className={styles['tooltip-wrapper']}
    >
      <div
        className={styles['tooltip-wrapper-title']}
        style={{
          top: `-${height + 10}px`,
          opacity: showTooltip ? '1' : '0',
        }}
        id={tooltipId}
      >
        {title}
      </div>
      {children}
    </div>
  )
}

export default TooltipWrapper

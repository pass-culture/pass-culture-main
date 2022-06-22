import React, { useCallback, useEffect, useState } from 'react'

import cn from 'classnames'
import styles from './Toggle.module.scss'

interface IToggle {
  isActiveByDefault?: boolean
  isDisabled?: boolean
  label: string
  handleClick?: () => void
}

const Toggle = ({
  isActiveByDefault = false,
  isDisabled = false,
  label = 'Label',
  handleClick,
}: IToggle) => {
  const [isActive, setIsActive] = useState(isActiveByDefault)

  useEffect(() => {
    setIsActive(isActiveByDefault)
  }, [isActiveByDefault])

  const onClick = useCallback(() => {
    setIsActive(!isActive)
    handleClick && handleClick()
  }, [isActive, setIsActive, handleClick])

  return (
    <button
      className={cn(styles['Toggle'])}
      type="button"
      disabled={isDisabled}
      aria-pressed={isActive}
      onClick={onClick}
    >
      {label}
      <span className={cn(styles['ToggleDisplay'])} hidden />
    </button>
  )
}
export default Toggle

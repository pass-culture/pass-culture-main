import cn from 'classnames'
import React, { useCallback, useEffect, useState } from 'react'

import styles from './Toggle.module.scss'

/**
 * Props for the Toggle component.
 */
export interface ToggleProps {
  /**
   * Indicates if the toggle is active by default.
   * @default false
   */
  isActiveByDefault?: boolean
  /**
   * Indicates if the toggle is disabled.
   * @default false
   */
  isDisabled?: boolean
  /**
   * The label text for the toggle.
   */
  label: string
  /**
   * Callback function triggered when the toggle is clicked.
   */
  handleClick?: () => void
}

/**
 * The Toggle component is used to render a button that represents an on/off state.
 * It allows users to control a setting between two states (active/inactive).
 *
 * ---
 * **Important: Use `isActiveByDefault` to initialize the state and `handleClick` to handle changes in the toggle state.**
 * ---
 *
 * @param {ToggleProps} props - The props for the Toggle component.
 * @returns {JSX.Element} The rendered Toggle component.
 *
 * @example
 * <Toggle
 *   label="Enable Notifications"
 *   isActiveByDefault={true}
 *   handleClick={() => console.log('Toggle clicked')}
 * />
 *
 * @accessibility
 * - **Aria-Pressed**: The button uses the `aria-pressed` attribute to indicate its current state to assistive technologies.
 * - **Labeling**: Ensure the `label` prop is descriptive to inform users of the toggle's purpose.
 */
export const Toggle = ({
  isActiveByDefault = false,
  isDisabled = false,
  label = 'Label',
  handleClick,
}: ToggleProps) => {
  const [isActive, setIsActive] = useState(isActiveByDefault)

  useEffect(() => {
    setIsActive(isActiveByDefault)
  }, [isActiveByDefault])

  const onClick = useCallback(() => {
    setIsActive(!isActive)
    handleClick?.()
  }, [isActive, handleClick])

  return (
    <button
      className={cn(styles['toggle'])}
      type="button"
      disabled={isDisabled}
      aria-pressed={isActive}
      onClick={onClick}
    >
      {label}
      <span className={cn(styles['toggle-display'])} hidden />
    </button>
  )
}

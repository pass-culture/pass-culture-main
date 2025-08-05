import cn from 'classnames'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import React from 'react'
import { SharedButtonProps } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ButtonFilter.module.scss'

/**
 * Props for the Button component.
 *
 * @extends SharedButtonProps, React.ButtonHTMLAttributes<HTMLButtonElement>
 */
interface ButtonFilterProps
  extends SharedButtonProps,
    React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Whether the button is open.
   */
  isOpen?: boolean
  /**
   * Whether the button is active.
   * @default false
   */
  isActive?: boolean
}

/**
 * The Button filter component provides a customizable button element.
 *
 * ---
 * **Important: Ensure to use descriptive labels for buttons to improve accessibility.**
 * When using icons only, make sure to provide an accessible label or `aria-label`.
 * ---
 *
 * @param {ButtonFilterProps} props - The props for the Button component.
 * @returns {JSX.Element} The rendered Button component.
 *
 * @example
 * <ButtonFilter
 *   isOpen={false}
 *   isActive={false}
 *   disabled
 * >
 *   Filtrer
 * </ButtonFilter>
 *
 * @accessibility
 * - **Keyboard Navigation**: The button can be focused and activated using the keyboard, ensuring it meets accessibility standards for interactive elements.
 */
export const ButtonFilter = ({
  className,
  children,
  isOpen = false,
  isActive = false,
  type = 'button',
  testId,
  ...buttonAttrs
}: ButtonFilterProps): JSX.Element => {
  return (
    <button
      className={cn(
        styles['button-filter'],
        { [styles[`button-filter-open`]]: isOpen },
        { [styles[`button-filter-active`]]: isActive },
        className
      )}
      type={type}
      data-testid={testId}
      {...buttonAttrs}
    >
      {children}
      <SvgIcon
        src={isOpen ? fullUpIcon : fullDownIcon}
        alt={'Ouvert/Fermé'}
        className={styles['button-filter-icon']}
        width="20"
      />
    </button>
  )
}

ButtonFilter.displayName = 'ButtonFilter'

/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React, { ForwardedRef, forwardRef } from 'react'

import strokePassIcon from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

/**
 * Props for the Button component.
 *
 * @extends SharedButtonProps, React.ButtonHTMLAttributes<HTMLButtonElement>
 */
export interface ButtonProps
  extends SharedButtonProps,
    React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Whether the button has a tooltip.
   */
  hasTooltip?: boolean
  /**
   * Whether the button is in a loading state.
   * @default false
   */
  isLoading?: boolean
  /**
   * Custom class name for the tooltip content.
   */
  tooltipContentClassName?: string
  /**
   * Custom class name for the icon.
   */
  iconClassName?: string
}

/**
 * The Button component provides a customizable button element that can include icons, tooltips, and loading states.
 * It supports various styles through the `variant` prop and can display icons on either side of the button text.
 *
 * ---
 * **Important: Ensure to use descriptive labels for buttons to improve accessibility.**
 * When using icons only, make sure to provide an accessible label or `aria-label`.
 * ---
 *
 * @param {ButtonProps} props - The props for the Button component.
 * @returns {JSX.Element} The rendered Button component.
 *
 * @example
 * <Button
 *   variant={ButtonVariant.PRIMARY}
 *   icon={strokePassIcon}
 *   iconAlt="Submit Icon"
 *   isLoading={true}
 *   hasTooltip={true}
 * >
 *   Submit
 * </Button>
 *
 * @accessibility
 * - **Loading State**: When `isLoading` is true, a spinner icon is displayed to indicate the button's loading state.
 * - **Tooltip Support**: The `Tooltip` component is used to display additional information. Ensure that the tooltip content is meaningful and helpful for users.
 * - **Keyboard Navigation**: The button can be focused and activated using the keyboard, ensuring it meets accessibility standards for interactive elements.
 */
export const Button = forwardRef(
  (
    {
      className,
      children,
      icon,
      iconClassName,
      iconAlt,
      iconPosition = IconPositionEnum.LEFT,
      variant = ButtonVariant.PRIMARY,
      type = 'button',
      hasTooltip,
      testId,
      isLoading = false,
      disabled,
      tooltipContentClassName,
      ...buttonAttrs
    }: ButtonProps,
    buttonRef: ForwardedRef<HTMLButtonElement>
  ): JSX.Element => {
    const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)
    const loadingDiv = (
      <div className={styles['spinner-icon']} data-testid="spinner">
        <SvgIcon src={strokePassIcon} alt="" />
      </div>
    )
    const content = (
      <>
        {icon && !isLoading && iconPosition !== IconPositionEnum.RIGHT && (
          <SvgIcon
            src={icon}
            alt={iconAlt}
            className={cn(styles['button-icon'], iconClassName, {
              [styles['has-tooltip']]: hasTooltip,
            })}
            width="20"
          />
        )}
        {variant === ButtonVariant.BOX ? (
          <div className={styles['button-arrow-content']} />
        ) : (
          <>
            {isLoading && loadingDiv}
            {!isLoading && !hasTooltip && children}
          </>
        )}

        {icon && !isLoading && iconPosition === IconPositionEnum.RIGHT && (
          <SvgIcon
            src={icon}
            alt={iconAlt}
            className={cn(styles['button-icon'], iconClassName)}
            width="20"
          />
        )}
      </>
    )

    return (
      <button
        className={cn(
          styles['button'],
          styles[`button-${variant}`],
          styles[`button-${iconPosition}`],
          { [styles['loading-spinner']]: isLoading },
          className
        )}
        type={type}
        data-testid={testId}
        disabled={disabled || isLoading}
        {...buttonAttrs}
        {...(hasTooltip && tooltipProps)}
        ref={buttonRef}
      >
        {hasTooltip ? (
          <Tooltip
            content={children}
            visuallyHidden={isTooltipHidden}
            tooltipContentClassName={tooltipContentClassName}
          >
            {content}
          </Tooltip>
        ) : (
          content
        )}
      </button>
    )
  }
)
Button.displayName = 'Button'

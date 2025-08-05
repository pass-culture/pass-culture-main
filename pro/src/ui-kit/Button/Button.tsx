/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import strokePassIcon from 'icons/stroke-pass.svg'
import React, { ForwardedRef, forwardRef } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip, TooltipProps } from 'ui-kit/Tooltip/Tooltip'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export interface ButtonProps
  extends SharedButtonProps,
    Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'title'> {
  isLoading?: boolean
  tooltipContent?: TooltipProps['content']
  iconClassName?: string
}

/**
 * The Button component provides a customizable button element that can include icons, tooltips, and loading states.
 * It supports various styles through the `variant` prop and can display icons on either side of the button text.
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
 * - Ensure to use descriptive labels for buttons to improve accessibility.
 * - When using an icons as content for the button, make sure to provide an accessible label with the `iconAlt` prop.
 * - The `Tooltip` component is used to display additional information. Ensure that the tooltip content is meaningful and helpful for users.
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
      testId,
      isLoading = false,
      disabled,
      tooltipContent,
      ...buttonAttrs
    }: ButtonProps,
    buttonRef: ForwardedRef<HTMLButtonElement>
  ): JSX.Element => {
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
              [styles['has-tooltip']]: Boolean(tooltipContent),
            })}
            width="20"
          />
        )}
        <>
          {isLoading && loadingDiv}
          {children}
        </>
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

    const button = (
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
        ref={buttonRef}
      >
        {content}
      </button>
    )

    return !tooltipContent ? (
      button
    ) : (
      <Tooltip content={tooltipContent}>{button}</Tooltip>
    )
  }
)
Button.displayName = 'Button'

import classNames from 'classnames'
import { type ForwardedRef, forwardRef, type MouseEventHandler } from 'react'
import { Link } from 'react-router'

import loadingIcon from '@/icons/stroke-pass.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Button.module.scss'
import type { ButtonProps } from './types'
import {
  ButtonColor,
  ButtonSize,
  ButtonType,
  ButtonVariant,
  IconPositionEnum,
} from './types'

const ICON_WIDTH = {
  [ButtonSize.DEFAULT]: '16',
  [ButtonSize.SMALL]: '14',
}

export const Button = forwardRef<
  HTMLButtonElement | HTMLAnchorElement,
  ButtonProps
>(
  (
    {
      color = ButtonColor.BRAND,
      variant = ButtonVariant.PRIMARY,
      label,
      disabled,
      hovered = false,
      isLoading,
      size = ButtonSize.DEFAULT,
      type = ButtonType.BUTTON,
      transparent = false,
      fullWidth = false,
      /***** Icon props *****/
      icon,
      iconAlt,
      iconPosition = IconPositionEnum.LEFT,
      iconClassName,
      /***** Link props *****/
      opensInNewTab = false,
      to = '',
      isExternal = false,
      isSectionLink = false,
      ...props
    }: ButtonProps,
    ref
  ): JSX.Element => {
    const getClassNames = (): string => {
      return classNames(
        styles.button,
        styles[`btn-${color}`],
        styles[`btn-${variant}`],
        styles[`btn-${size}`],
        icon &&
          iconPosition === IconPositionEnum.CENTER &&
          styles['btn-icon-only'],
        hovered && styles['btn-hovered'],
        disabled && styles['btn-disabled'],
        isLoading && styles['btn-loading'],
        transparent && styles['btn-transparent'],
        fullWidth && styles['btn-full-width']
      )
    }

    const renderIcon = () =>
      icon && (
        <SvgIcon
          src={icon}
          alt={iconAlt}
          className={`${styles['btn-icon']} ${iconClassName}`}
          width={ICON_WIDTH[size as ButtonSize]}
        />
      )

    const renderSpinner = (withLabel = false) => (
      <>
        <div className={styles['spinner-icon']} data-testid="spinner">
          <SvgIcon
            src={loadingIcon}
            alt="Loading"
            width={ICON_WIDTH[size as ButtonSize]}
            className={styles['spinner-svg']}
          />
        </div>
        {withLabel && label}
      </>
    )

    const getContent = () => {
      // Loading state
      if (isLoading) {
        return renderSpinner(
          iconPosition !== IconPositionEnum.CENTER && !!label
        )
      }

      // Only icon in center
      if (icon && iconPosition === IconPositionEnum.CENTER) {
        return renderIcon()
      }

      // Label with icon (left or right)
      if (label && icon) {
        return (
          <>
            {iconPosition === IconPositionEnum.LEFT && renderIcon()}
            {label}
            {iconPosition === IconPositionEnum.RIGHT && renderIcon()}
          </>
        )
      }

      // Only label
      return label
    }

    const content = getContent()
    const classNamesString = getClassNames()

    // If `to` is provided, render a link instead of a button
    if (to) {
      const { onClick, onBlur, ...restProps } = props

      const commonProps = {
        className: classNamesString,
        onClick: onClick as MouseEventHandler<HTMLAnchorElement> | undefined,
        onBlur: onBlur as
          | ((e: React.FocusEvent<HTMLAnchorElement>) => void)
          | undefined,
        'aria-label': props['aria-label'],
        target: opensInNewTab ? '_blank' : undefined,
      }

      if (isSectionLink || isExternal) {
        return (
          <a
            href={to}
            rel="noopener noreferrer"
            ref={ref as ForwardedRef<HTMLAnchorElement>}
            {...commonProps}
            {...(restProps as React.AnchorHTMLAttributes<HTMLAnchorElement>)}
          >
            {content}
          </a>
        )
      }

      return (
        <Link
          to={to}
          ref={ref as ForwardedRef<HTMLAnchorElement>}
          {...commonProps}
          {...(restProps as Omit<React.ComponentProps<typeof Link>, 'to'>)}
        >
          {content}
        </Link>
      )
    }

    // By default, render a button
    return (
      <button
        className={classNamesString}
        {...props}
        disabled={disabled || isLoading}
        type={type}
        ref={ref as ForwardedRef<HTMLButtonElement>}
      >
        {content}
      </button>
    )
  }
)

import classNames from 'classnames'
import { forwardRef } from 'react'

import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

import styles from './Button.module.scss'
import { Icon } from './components/Icon/Icon'
import { Spinner } from './components/Spinner/Spinner'
import type { ButtonProps } from './types'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from './types'
import { getComponentProps, getComponentType } from './utils/helpers'

export const Button = forwardRef<
  HTMLButtonElement | HTMLAnchorElement,
  Readonly<ButtonProps>
>(
  (
    {
      as = 'button',
      color = ButtonColor.BRAND,
      variant = ButtonVariant.PRIMARY,
      label,
      disabled,
      hovered = false,
      isLoading,
      size = ButtonSize.DEFAULT,
      transparent = false,
      fullWidth = false,
      fullHeight = false,
      tooltip,
      type = 'button',
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
    const className = classNames(
      styles.button,
      styles[`btn-${color}`],
      styles[`btn-${variant}`],
      styles[`btn-${size}`],
      {
        [styles['btn-icon-only']]: icon && !label,
        [styles['btn-hovered']]: hovered,
        [styles['btn-disabled']]: disabled,
        [styles['btn-loading']]: isLoading,
        [styles['btn-transparent']]: transparent,
        [styles['btn-full-width']]: fullWidth,
        [styles['btn-full-height']]: fullHeight,
      }
    )

    const absoluteUrl =
      isSectionLink || isExternal || to.startsWith('/') ? to : `/${to}`

    const Component = getComponentType(as, isExternal, isSectionLink)
    const componentProps = getComponentProps(
      Component,
      type,
      absoluteUrl,
      disabled,
      isLoading,
      opensInNewTab
    )

    const iconElement = icon && !isLoading && (
      <Icon
        icon={icon}
        iconAlt={iconAlt}
        className={styles['btn-icon']}
        iconClassName={iconClassName}
      />
    )

    const contentElement = (
      <>
        {iconPosition === IconPositionEnum.LEFT && iconElement}
        {isLoading && <Spinner />}
        {label && <span className={styles['btn-label']}>{label}</span>}
        {iconPosition === IconPositionEnum.RIGHT && iconElement}
      </>
    )

    const buttonElement = (
      <Component ref={ref} className={className} {...componentProps} {...props}>
        {contentElement}
      </Component>
    )

    return tooltip && !disabled ? (
      <Tooltip content={tooltip}>{buttonElement}</Tooltip>
    ) : (
      buttonElement
    )
  }
)

Button.displayName = 'Button'

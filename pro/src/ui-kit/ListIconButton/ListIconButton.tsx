/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React, { MouseEvent, forwardRef, ForwardedRef } from 'react'
import { Link } from 'react-router'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './ListIconButton.module.scss'

export enum ListIconButtonVariant {
  DEFAULT = 'default',
  PRIMARY = 'primary',
}

/**
 * Props for the ListIconButton component.
 */
interface ListIconButtonProps extends React.HTMLProps<HTMLButtonElement> {
  /**
   * The icon to display inside the button.
   */
  icon: string
  /**
   * The variant of the button.
   * @default ListIconButtonVariant.DEFAULT
   */
  variant?: ListIconButtonVariant
  /**
   * Custom CSS class for additional styling of the button.
   */
  className?: string
  /**
   * Custom CSS class for the tooltip content.
   */
  tooltipContentClassName?: string
  /**
   * Callback function triggered when the button is clicked.
   */
  onClick?: (event: MouseEvent) => void
  /**
   * The URL to navigate to when the button is clicked.
   */
  url?: string
  /**
   * Indicates if the link is external.
   * @default true
   */
  isExternal?: boolean
  /**
   * Custom test ID for targeting the component in tests.
   */
  dataTestid?: string
  /**
   * Target attribute for the <a> tag
   */
  target?: string
}

const LIST_ICON_SIZE = '16'

/**
 * The ListIconButton component is used to render an icon button that can be used as a link or a button.
 * It supports tooltips, external/internal links, and different button variants.
 *
 * ---
 * **Important: Use the `url` prop to create a link button, and the `onClick` prop to handle button actions.**
 * ---
 *
 * @param {ListIconButtonProps} props - The props for the ListIconButton component.
 * @returns {JSX.Element} The rendered ListIconButton component.
 *
 * @example
 * <ListIconButton
 *   icon="/icons/edit.svg"
 *   variant={ListIconButtonVariant.PRIMARY}
 *   onClick={() => console.log('Button clicked')}
 * />
 *
 * @accessibility
 * - **Tooltip**: The button includes a tooltip for additional context, which is hidden when not needed.
 * - **Keyboard Navigation**: The button and link can be focused and activated using the keyboard, ensuring accessibility.
 */
export const ListIconButton = forwardRef(
  (
    {
      children,
      className,
      variant = ListIconButtonVariant.DEFAULT,
      tooltipContentClassName,
      icon,
      onClick,
      url,
      isExternal = true,
      dataTestid,
      target,
      ...buttonAttrs
    }: ListIconButtonProps,
    forwadedRef: ForwardedRef<HTMLButtonElement>
  ): JSX.Element => {
    const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)

    const svgicon = (
      <SvgIcon
        src={icon}
        alt=""
        className={cn(styles['button-icon'])}
        width={LIST_ICON_SIZE}
      />
    )
    const content = !buttonAttrs.disabled ? (
      <Tooltip
        content={children}
        tooltipContainerClassName={styles['tooltip']}
        tooltipContentClassName={tooltipContentClassName}
        visuallyHidden={isTooltipHidden}
      >
        {svgicon}
      </Tooltip>
    ) : (
      svgicon
    )

    const button = (
      <button
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        ref={forwadedRef}
        {...buttonAttrs}
        onClick={onClick}
        type="button"
        data-testid={dataTestid}
        {...tooltipProps}
      >
        {content}
      </button>
    )

    const link = isExternal ? (
      <a
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        href={url}
        onClick={onClick}
        target={target}
        rel={target === '_blank' ? 'noreferrer' : undefined}
        {...tooltipProps}
      >
        {content}
      </a>
    ) : (
      <Link
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        onClick={onClick}
        to={`${url}`}
        {...tooltipProps}
      >
        {content}
      </Link>
    )

    return url ? link : button
  }
)

ListIconButton.displayName = 'ListIconButton'

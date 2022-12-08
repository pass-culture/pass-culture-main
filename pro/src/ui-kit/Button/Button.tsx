/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React from 'react'

import { ReactComponent as IcoArrowRight } from 'icons/ico-mini-arrow-right.svg'
import Tooltip from 'ui-kit/Tooltip'
import { uniqId } from 'utils/uniqId'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

interface IButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  hasTooltip?: boolean
}

const Button = ({
  className,
  children,
  Icon,
  iconPosition = IconPositionEnum.LEFT,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  innerRef,
  hasTooltip,
  ...buttonAttrs
}: IButtonProps): JSX.Element => {
  const tooltipId = uniqId()

  const button = (
    <button
      className={cn(
        styles['button'],
        styles[`button-${variant}`],
        styles[`button-${iconPosition}`],
        className
      )}
      ref={innerRef}
      type={type}
      {...(hasTooltip ? { 'aria-describedBy': tooltipId } : {})}
      {...buttonAttrs}
    >
      {Icon && iconPosition !== IconPositionEnum.RIGHT && (
        <Icon className={styles['button-icon']} />
      )}
      {hasTooltip ? (
        <div className={styles['visually-hidden']}>{children}</div>
      ) : variant === ButtonVariant.BOX ? (
        <div className={styles['button-arrow-content']}>{children}</div>
      ) : (
        children
      )}
      {Icon && iconPosition === IconPositionEnum.RIGHT && (
        <Icon className={styles['button-icon']} />
      )}
      {variant === ButtonVariant.BOX && (
        <IcoArrowRight
          className={cn(styles['button-icon'], styles['button-icon-arrow'])}
        />
      )}
    </button>
  )

  if (hasTooltip) {
    return (
      <Tooltip id={tooltipId} content={children}>
        {button}
      </Tooltip>
    )
  }

  return button
}

export default Button

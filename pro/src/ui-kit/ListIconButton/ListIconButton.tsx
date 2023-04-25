/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React, { FunctionComponent, SVGProps, useId } from 'react'

import Tooltip from 'ui-kit/Tooltip'

import styles from './ListIconButton.module.scss'

export interface IListIconButtonProps
  extends React.HTMLProps<HTMLButtonElement> {
  Icon: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  hasTooltip?: boolean
  onClick?: () => void
  url?: string
}

const ListIconButton = ({
  children,
  className,
  Icon,
  innerRef,
  hasTooltip,
  onClick,
  url,
  ...buttonAttrs
}: IListIconButtonProps): JSX.Element => {
  const tooltipId = useId()
  const button = (
    <button
      className={cn(styles['button'], className)}
      ref={innerRef}
      {...buttonAttrs}
      onClick={onClick}
      type="button"
    >
      <Icon className={cn(styles['button-icon'])} />
      <div className={styles['visually-hidden']}>{children}</div>
    </button>
  )
  const link = (
    <a className={cn(styles['button'], className)} href={url} onClick={onClick}>
      <Icon className={cn(styles['button-icon'])} />
      <div className={styles['visually-hidden']}>{children}</div>
    </a>
  )
  if (hasTooltip && !buttonAttrs?.disabled) {
    return (
      <Tooltip id={tooltipId} content={children} className={styles['tooltip']}>
        {url ? link : button}
      </Tooltip>
    )
  }
  return button
}

export default ListIconButton

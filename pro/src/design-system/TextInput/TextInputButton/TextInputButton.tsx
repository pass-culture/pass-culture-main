import type { FocusEventHandler, MouseEventHandler } from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

import styles from './TextInputButton.module.scss'

export type TextInputButtonProps = {
  icon: string
  label: string
  onClick: MouseEventHandler<HTMLButtonElement>
  onBlur?: FocusEventHandler<HTMLButtonElement>
  disabled?: boolean
}

export function TextInputButton({
  icon,
  label,
  onClick,
  onBlur,
  disabled,
}: TextInputButtonProps) {
  return (
    <Tooltip content={label}>
      <button
        className={styles['button']}
        type="button"
        onClick={onClick}
        onBlur={onBlur}
        disabled={disabled}
      >
        <SvgIcon src={icon} alt={label} className={styles['button-icon']} />
      </button>
    </Tooltip>
  )
}

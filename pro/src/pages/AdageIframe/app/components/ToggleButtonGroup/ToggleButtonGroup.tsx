import cn from 'classnames'
import type { MouseEvent } from 'react'

import styles from './ToggleButtonGroup.module.scss'
import { ToggleButtonGroupButton } from './ToggleButtonGroupButton/ToggleButtonGroupButton'

export type ToggleButton = {
  label: string
  id: string
  content: JSX.Element
  onClick: (button: ToggleButton, event: MouseEvent) => void
  disabled?: boolean
}

type ToggleButtonGroupProps = {
  groupLabel: string
  buttons: ToggleButton[]
  activeButton: string
  className?: string
}

export function ToggleButtonGroup({
  groupLabel,
  buttons,
  activeButton,
  className,
}: ToggleButtonGroupProps) {
  return (
    // biome-ignore lint/a11y/useSemanticElements: We don't want to use a `<fieldset />` here.
    <div
      role="group"
      aria-label={groupLabel}
      className={cn(styles['button-group'], className)}
    >
      {buttons.map((button) => (
        <ToggleButtonGroupButton
          button={button}
          isActive={button.id === activeButton}
          key={button.id}
        />
      ))}
    </div>
  )
}

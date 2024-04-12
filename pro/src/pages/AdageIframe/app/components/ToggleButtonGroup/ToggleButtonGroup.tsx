import { MouseEvent } from 'react'

import styles from './ToggleButtonGroup.module.scss'
import ToggleButtonGroupButton from './ToggleButtonGroupButton/ToggleButtonGroupButton'

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
}

export default function ToggleButtonGroup({
  groupLabel,
  buttons,
  activeButton,
}: ToggleButtonGroupProps) {
  return (
    <div
      role="group"
      aria-label={groupLabel}
      className={styles['button-group']}
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

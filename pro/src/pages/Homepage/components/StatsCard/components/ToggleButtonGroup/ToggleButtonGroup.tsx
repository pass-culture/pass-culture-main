import { Icon } from 'design-system/Button/components/Icon/Icon'
import { useState } from 'react'

import fullCheckIcon from '@/icons/full-check.svg'

import styles from './ToggleButtonGroup.module.scss'

type ToggleSideProps = {
  id: string
  label: string
  icon?: string
  iconAlt?: string
  selected?: boolean
  handleClick?: () => void
  controls: string
}

export interface ToggleButtonGroupProps {
  left: ToggleSideProps
  right: ToggleSideProps
  selected: 'left' | 'right'
}

export const ToggleButtonGroup = ({
  left,
  right,
  selected,
}: ToggleButtonGroupProps) => {
  const [activeState, setActiveState] = useState(
    selected === 'left' ? left.id : right.id
  )

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    let nextSelected: ToggleSideProps | null = null

    switch (event.key) {
      case 'ArrowRight':
      case 'End':
        nextSelected = right
        break
      case 'ArrowLeft':
      case 'Home':
        nextSelected = left
        break
      default:
        return
    }

    event.preventDefault()
    if (nextSelected) {
      nextSelected.handleClick?.()
      setActiveState(nextSelected.id)
    }
  }

  return (
    <div className={styles['btn-group']} role="tablist">
      <button
        id={left.id}
        type="button"
        role="tab"
        aria-controls={left.controls}
        aria-selected={activeState === left.id}
        onClick={() => {
          if (activeState === right.id) {
            setActiveState(left.id)
            left.handleClick?.()
          }
        }}
        onKeyDown={handleKeyDown}
        className={styles['btn-group-btn']}
      >
        {activeState === left.id && (
          <Icon icon={fullCheckIcon} className={styles['btn-group-btn-icon']} />
        )}
        {left.icon && (
          <Icon
            icon={left.icon}
            iconAlt={left.iconAlt}
            className={styles['btn-group-btn-icon']}
          />
        )}
        <p>{left.label}</p>
      </button>
      <button
        id={right.id}
        role="tab"
        aria-controls={right.controls}
        aria-selected={activeState === right.id}
        type="button"
        onClick={() => {
          if (activeState === left.id) {
            setActiveState(right.id)
            right.handleClick?.()
          }
        }}
        onKeyDown={handleKeyDown}
        className={styles['btn-group-btn']}
      >
        {activeState === right.id && (
          <Icon icon={fullCheckIcon} className={styles['btn-group-btn-icon']} />
        )}
        {right.icon && (
          <Icon
            icon={right.icon}
            iconAlt={right.iconAlt}
            className={styles['btn-group-btn-icon']}
          />
        )}
        <p>{right.label}</p>
      </button>
    </div>
  )
}

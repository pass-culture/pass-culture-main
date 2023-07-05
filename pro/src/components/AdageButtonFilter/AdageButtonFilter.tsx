import cn from 'classnames'
import React, { useRef, useState } from 'react'

import useOnClickOrFocusOutside from 'hooks/useOnClickOrFocusOutside'

import styles from './AdageButtonFilter.module.scss'

export interface AdageButtonFilterProps
  extends React.HTMLProps<HTMLButtonElement> {
  title: string
  isActive: boolean
  itemsLength?: number
}

const AdageButtonFilter = ({
  title,
  children,
  isActive,
  disabled,
  itemsLength,
}: AdageButtonFilterProps): JSX.Element => {
  const [filterModal, setFilterModal] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)

  useOnClickOrFocusOutside(containerRef, () => {
    setFilterModal(false)
  })

  return (
    <div ref={containerRef} className={styles['adage-container']}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setFilterModal(!filterModal)}
        className={cn([styles['adage-button']], {
          [styles['adage-button-is-active']]: isActive,
          [styles['adage-button-selected']]: filterModal,
        })}
      >
        <div
          className={cn({
            [styles['adage-button-active']]: isActive,
            [styles['adage-button-active-disabled']]: disabled,
          })}
        ></div>
        {title} {isActive && `(${itemsLength})`}
      </button>

      <dialog open={filterModal} className={styles['adage-button-children']}>
        {children}
      </dialog>
    </div>
  )
}

export default AdageButtonFilter

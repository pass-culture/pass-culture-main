import cn from 'classnames'
import React, { useCallback, useEffect, useRef, useState } from 'react'

import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageButtonFilter.module.scss'

export interface AdageButtonFilterProps
  extends React.HTMLProps<HTMLButtonElement> {
  title: string
  isActive: boolean
  itemsLength?: number | null
  isOpen: boolean
  setIsOpen: React.Dispatch<React.SetStateAction<{ [key: string]: boolean }>>
  filterName: string
  handleSubmit: () => void
}

export const AdageButtonFilter = ({
  title,
  children,
  isActive,
  disabled,
  itemsLength,
  isOpen,
  setIsOpen,
  filterName,
  handleSubmit,
}: AdageButtonFilterProps): JSX.Element => {
  const [dialogLeftOffset, setDialogLeftOffset] = useState(0)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const dialogRef = useRef<HTMLDialogElement | null>(null)

  useEffect(() => {
    const containerElm = containerRef.current
    const dialogElm = dialogRef.current

    //  Only reposition when opening the dialog
    if (!isOpen || !containerElm || !dialogElm) {
      return
    }

    //  Part of the dialog width that goes beyond the body width on the right
    const dialogOutOfScreenDistance =
      containerElm.getBoundingClientRect().left +
      dialogElm.getBoundingClientRect().width -
      document.body.clientWidth

    setDialogLeftOffset(Math.max(dialogOutOfScreenDistance, 0))
  }, [isOpen])

  const handleClickOutside = useCallback(
    (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        if (isOpen) {
          setIsOpen({ [filterName]: false })
          handleSubmit()
        }
      }
    },
    [setIsOpen, handleSubmit, isOpen, filterName]
  )

  useEffect(() => {
    if (containerRef.current) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [containerRef, handleClickOutside])

  const clickModalButtonHandler = () => {
    setIsOpen((previousIsOpen) => ({
      [filterName]: !previousIsOpen[filterName],
    }))
  }

  return (
    <div ref={containerRef} className={styles['adage-container']}>
      <button
        type="button"
        disabled={disabled}
        onClick={clickModalButtonHandler}
        className={cn([styles['adage-button']], {
          [styles['adage-button-is-active']]: isActive,
          [styles['adage-button-selected']]: isOpen,
        })}
      >
        {title} {isActive && `(${itemsLength})`}
        {!disabled && (
          <SvgIcon
            className={styles['adage-button-dropdown']}
            alt=""
            src={isOpen ? fullUpIcon : fullDownIcon}
            width="16"
          />
        )}
      </button>

      <div className={styles['adage-button-modal']}>
        <dialog
          open={isOpen}
          className={styles['adage-button-children']}
          style={{ left: `${-dialogLeftOffset}px` }}
          ref={dialogRef}
        >
          {children}
        </dialog>
      </div>
    </div>
  )
}

import cn from 'classnames'
import React, { useCallback, useEffect, useRef } from 'react'

import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SearchFormValues } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/OfferFilters/OfferFilters'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageButtonFilter.module.scss'

export interface AdageButtonFilterProps
  extends React.HTMLProps<HTMLButtonElement> {
  title: string
  isActive: boolean
  itemsLength?: number
  isOpen: boolean
  setIsOpen: (value: { [key: string]: boolean }) => void
  filterName: string
  handleSubmit: (value: SearchFormValues) => void
  formikValues: SearchFormValues
}

const AdageButtonFilter = ({
  title,
  children,
  isActive,
  disabled,
  itemsLength,
  isOpen,
  setIsOpen,
  filterName,
  handleSubmit,
  formikValues,
}: AdageButtonFilterProps): JSX.Element => {
  const containerRef = useRef<HTMLDivElement | null>(null)

  const handleClickOutside = useCallback(
    (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        if (isOpen) {
          setIsOpen({ [filterName]: false })
          handleSubmit(formikValues)
        }
      }
    },
    [setIsOpen, handleSubmit]
  )

  useEffect(() => {
    if (containerRef.current) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [containerRef, handleClickOutside])

  const modalButton = () => {
    setIsOpen({ [filterName]: !isOpen })
  }

  return (
    <div ref={containerRef} className={styles['adage-container']}>
      <button
        type="button"
        disabled={disabled}
        onClick={modalButton}
        className={cn([styles['adage-button']], {
          [styles['adage-button-is-active']]: isActive,
          [styles['adage-button-selected']]: isOpen,
        })}
      >
        <div
          className={cn({
            [styles['adage-button-active']]: isActive,
            [styles['adage-button-active-disabled']]: disabled,
          })}
        ></div>
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
        <dialog open={isOpen} className={styles['adage-button-children']}>
          {children}
        </dialog>
      </div>
    </div>
  )
}

export default AdageButtonFilter

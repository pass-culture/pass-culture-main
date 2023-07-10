import cn from 'classnames'
import React, { useRef } from 'react'

import useOnClickOrFocusOutside from 'hooks/useOnClickOrFocusOutside'
import { SearchFormValues } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/OfferFilters/OfferFilters'

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

  useOnClickOrFocusOutside(containerRef, () => {
    setIsOpen({ [filterName]: false })
    handleSubmit(formikValues)
  })

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
      </button>

      <dialog open={isOpen} className={styles['adage-button-children']}>
        {children}
      </dialog>
    </div>
  )
}

export default AdageButtonFilter

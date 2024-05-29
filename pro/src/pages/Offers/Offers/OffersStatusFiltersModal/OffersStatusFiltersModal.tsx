import React, { useRef } from 'react'

import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'
import { useOnClickOrFocusOutside } from 'hooks/useOnClickOrFocusOutside'
import { Button } from 'ui-kit/Button/Button'
import { BaseRadio } from 'ui-kit/form/shared/BaseRadio/BaseRadio'

import {
  collectiveFilterStatus,
  individualFilterStatus,
} from '../OffersTableHead/StatusFiltersButton'

import styles from './OffersStatusFiltersModal.module.scss'

interface OfferStatusFiltersModalProps {
  applyFilters: () => void
  status?: SearchFiltersParams['status']
  setIsVisible: (isVisible: boolean) => void
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: string
}

export const OffersStatusFiltersModal = ({
  applyFilters,
  status,
  setIsVisible,
  updateStatusFilter,
  audience,
}: OfferStatusFiltersModalProps) => {
  const modalRef = useRef<HTMLDivElement | null>(null)

  useOnClickOrFocusOutside(modalRef, () => setIsVisible(false))

  const handleClick = () => {
    setIsVisible(false)
    applyFilters()
  }

  const filters =
    audience === Audience.INDIVIDUAL
      ? individualFilterStatus
      : collectiveFilterStatus
  return (
    <div
      className={styles['offers-status-filters']}
      ref={modalRef}
      id="offer-status-filters-modal"
    >
      <fieldset>
        <legend className={styles['osf-title']}>Afficher les offres</legend>
        {filters.map(({ label, value }) => (
          <BaseRadio
            key={value}
            label={label}
            name="status"
            value={value}
            checked={status === value}
            className={styles['radio']}
            onChange={(event) =>
              updateStatusFilter(
                event.target.value as SearchFiltersParams['status']
              )
            }
          />
        ))}
      </fieldset>

      <Button
        className={styles['button']}
        onClick={handleClick}
        aria-label="Appliquer les filtres"
      >
        Appliquer
      </Button>
    </div>
  )
}

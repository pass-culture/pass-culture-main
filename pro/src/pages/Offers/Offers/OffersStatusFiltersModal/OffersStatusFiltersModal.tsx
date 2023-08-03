import React, { useRef } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { ALL_STATUS } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared'
import useOnClickOrFocusOutside from 'hooks/useOnClickOrFocusOutside'
import { RadioInput } from 'ui-kit/form_raw/RadioInput/RadioInput'

interface OfferStatusFiltersModalProps {
  isVisible: boolean
  applyFilters: () => void
  status?: SearchFiltersParams['status']
  setIsVisible: (isVisible: boolean) => void
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: string
}

export const OffersStatusFiltersModal = ({
  isVisible,
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

  if (!isVisible) {
    return null
  }
  const filters =
    audience === Audience.INDIVIDUAL
      ? [
          { label: 'Toutes', value: ALL_STATUS },
          ...(audience === Audience.INDIVIDUAL
            ? [{ label: 'Brouillon', value: OfferStatus.DRAFT }]
            : []),
          { label: 'Publiée', value: OfferStatus.ACTIVE },
          { label: 'Désactivée', value: OfferStatus.INACTIVE },
          { label: 'Épuisée', value: OfferStatus.SOLD_OUT },
          { label: 'Expirée', value: OfferStatus.EXPIRED },
          { label: 'Validation en attente', value: OfferStatus.PENDING },
          { label: 'Refusée', value: OfferStatus.REJECTED },
        ]
      : [
          { label: 'Toutes', value: ALL_STATUS },
          { label: 'Désactivée', value: CollectiveOfferStatus.INACTIVE },
          { label: 'Expirée', value: CollectiveOfferStatus.EXPIRED },
          { label: 'Préréservée', value: CollectiveOfferStatus.PREBOOKED },
          { label: 'Publiée sur ADAGE', value: CollectiveOfferStatus.ACTIVE },
          {
            label: 'Refusée',
            value: CollectiveOfferStatus.REJECTED,
          },
          {
            label: 'Réservée',
            value: CollectiveOfferStatus.BOOKED,
          },
          { label: 'Terminée', value: CollectiveOfferStatus.ENDED },
          {
            label: 'Validation en attente',
            value: CollectiveOfferStatus.PENDING,
          },
        ]
  return (
    <div className="offers-status-filters" ref={modalRef}>
      <div className="osf-title">Afficher les offres</div>
      <>
        {filters.map(({ label, value }) => (
          <RadioInput
            checked={status === value}
            label={label}
            name="status"
            onChange={event =>
              updateStatusFilter(
                event.target.value as SearchFiltersParams['status']
              )
            }
            value={value}
            key={value}
          />
        ))}
      </>
      <button
        className="primary-button"
        onClick={handleClick}
        type="button"
        aria-label="appliquer les filtres"
      >
        Appliquer
      </button>
    </div>
  )
}

import React, { useCallback, useEffect, useRef } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { ALL_STATUS } from 'core/Offers/constants'
import { Audience } from 'core/shared'
import useActiveFeature from 'hooks/useActiveFeature'
import { RadioInput } from 'ui-kit/form_raw/RadioInput/RadioInput'

interface IOfferStatusFiltersModalProps {
  isVisible: boolean
  applyFilters: () => void
  status?: OfferStatus | CollectiveOfferStatus | 'all'
  setIsVisible: (isVisible: boolean) => void
  updateStatusFilter: (
    status: OfferStatus | CollectiveOfferStatus | 'all'
  ) => void
  audience: string
}

export const OffersStatusFiltersModal = ({
  isVisible,
  applyFilters,
  status,
  setIsVisible,
  updateStatusFilter,
  audience,
}: IOfferStatusFiltersModalProps) => {
  const modalRef = useRef<HTMLDivElement | null>(null)
  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  const handleStatusFilterChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      updateStatusFilter(
        event.target.value as OfferStatus | CollectiveOfferStatus | 'all'
      )
    },
    [updateStatusFilter]
  )

  const onClickOutside = useCallback(
    (event: MouseEvent): void => {
      if (
        modalRef.current &&
        !modalRef.current.contains(event.target as Node)
      ) {
        event.preventDefault()
        event.stopPropagation()

        setIsVisible(!isVisible)
      }
    },
    [setIsVisible, isVisible]
  )

  useEffect(() => {
    document.body.addEventListener('click', onClickOutside)

    return () => {
      document.body.removeEventListener('click', onClickOutside)
    }
  }, [onClickOutside])

  const handleClick = () => {
    setIsVisible(false)
    applyFilters()
  }

  if (!isVisible) {
    return null
  }
  const filters =
    audience === Audience.INDIVIDUAL || !isImproveCollectiveStatusActive
      ? [
          { label: 'Tous', value: ALL_STATUS },
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
          { label: 'Tous', value: ALL_STATUS },
          { label: 'Désactivée', value: CollectiveOfferStatus.INACTIVE },
          { label: 'Expirée', value: CollectiveOfferStatus.EXPIRED },
          { label: 'Publiée sur ADAGE', value: CollectiveOfferStatus.ACTIVE },
          { label: 'Préréservée', value: CollectiveOfferStatus.PREBOOKED },
          {
            label: 'Réservée',
            value: CollectiveOfferStatus.BOOKED,
          },
          { label: 'Terminée', value: CollectiveOfferStatus.ENDED },
          {
            label: 'Validation en attente',
            value: CollectiveOfferStatus.PENDING,
          },
          {
            label: 'Refusée',
            value: CollectiveOfferStatus.REJECTED,
          },
        ]
  return (
    <div className="offers-status-filters" ref={modalRef}>
      <div className="osf-title">Afficher les statuts</div>
      <>
        {filters.map(({ label, value }) => (
          <RadioInput
            checked={status === value}
            label={label}
            name="status"
            onChange={handleStatusFilterChange}
            value={value}
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

export default OffersStatusFiltersModal

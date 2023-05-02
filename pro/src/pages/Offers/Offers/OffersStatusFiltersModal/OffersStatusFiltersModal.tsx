import React, { useCallback, useEffect, useRef } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { ALL_STATUS } from 'core/Offers/constants'
import { Audience } from 'core/shared'
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
        setIsVisible(!isVisible)
      }
    },
    [setIsVisible, isVisible]
  )

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      document.addEventListener('click', onClickOutside, false)
    }, 0)
    return () => {
      clearTimeout(timeoutId)
      document.removeEventListener('click', onClickOutside, false)
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
            onChange={handleStatusFilterChange}
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

export default OffersStatusFiltersModal

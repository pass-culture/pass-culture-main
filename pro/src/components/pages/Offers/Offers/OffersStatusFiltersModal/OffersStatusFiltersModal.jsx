import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { ALL_STATUS } from 'core/Offers/constants'
import { Audience } from 'core/shared'
import useActiveFeature from 'hooks/useActiveFeature'
import { RadioInput } from 'ui-kit/form_raw/RadioInput/RadioInput'

export const OffersStatusFiltersModal = ({
  isVisible,
  applyFilters,
  status,
  setIsVisible,
  updateStatusFilter,
  audience,
}) => {
  const modalRef = useRef(null)
  const isDraftOfferEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')

  const handleStatusFilterChange = useCallback(
    event => {
      updateStatusFilter(event.target.value)
    },
    [updateStatusFilter]
  )

  const onClickOutside = useCallback(
    event => {
      const { target } = event
      if (modalRef.current && !modalRef.current.contains(target)) {
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

  return (
    <div className="offers-status-filters" ref={modalRef}>
      <div className="osf-title">Afficher les statuts</div>
      <RadioInput
        checked={status === ALL_STATUS}
        label="Tous"
        name="status"
        onChange={handleStatusFilterChange}
        value={ALL_STATUS}
      />
      {isDraftOfferEnabled && audience === Audience.INDIVIDUAL && (
        <RadioInput
          checked={status === OfferStatus.DRAFT}
          label="Brouillon"
          name="status"
          onChange={handleStatusFilterChange}
          value="DRAFT"
        />
      )}
      <RadioInput
        checked={status === OfferStatus.ACTIVE}
        label="Publiée"
        name="status"
        onChange={handleStatusFilterChange}
        value="ACTIVE"
      />
      <RadioInput
        checked={status === OfferStatus.INACTIVE}
        label="Désactivée"
        name="status"
        onChange={handleStatusFilterChange}
        value="INACTIVE"
      />
      <RadioInput
        checked={status === OfferStatus.SOLD_OUT}
        label="Épuisée"
        name="status"
        onChange={handleStatusFilterChange}
        value="SOLD_OUT"
      />
      <RadioInput
        checked={status === OfferStatus.EXPIRED}
        label="Expirée"
        name="status"
        onChange={handleStatusFilterChange}
        value="EXPIRED"
      />
      <RadioInput
        checked={status === OfferStatus.PENDING}
        label="Validation en attente"
        name="status"
        onChange={handleStatusFilterChange}
        value="PENDING"
      />
      <RadioInput
        checked={status === OfferStatus.REJECTED}
        label="Refusée"
        name="status"
        onChange={handleStatusFilterChange}
        value="REJECTED"
      />
      <button className="primary-button" onClick={handleClick} type="button">
        Appliquer
      </button>
    </div>
  )
}

OffersStatusFiltersModal.defaultProps = {
  status: null,
}

OffersStatusFiltersModal.propTypes = {
  applyFilters: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
  setIsVisible: PropTypes.func.isRequired,
  status: PropTypes.string,
  updateStatusFilter: PropTypes.func.isRequired,
}

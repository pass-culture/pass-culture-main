import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef } from 'react'

import { RadioInput } from 'components/layout/inputs/RadioInput/RadioInput'
import { ALL_STATUS } from 'components/pages/Offers/_constants'

export const OffersStatusFiltersModal = ({
  isVisible,
  refreshOffers,
  status,
  setIsVisible,
  updateStatusFilter,
}) => {
  const modalRef = useRef(null)

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

  if (!isVisible) {
    return null
  }

  return (
    <div
      className="offers-status-filters"
      ref={modalRef}
    >
      <div className="osf-title">
        {'Afficher les statuts'}
      </div>
      <RadioInput
        checked={status === ALL_STATUS}
        label="Tous"
        name="status"
        onChange={handleStatusFilterChange}
        value={ALL_STATUS}
      />
      <RadioInput
        checked={status === 'active'}
        label="Active"
        name="status"
        onChange={handleStatusFilterChange}
        value="active"
      />
      <RadioInput
        checked={status === 'inactive'}
        label="Inactive"
        name="status"
        onChange={handleStatusFilterChange}
        value="inactive"
      />
      <RadioInput
        checked={status === 'soldOut'}
        label="Épuisée"
        name="status"
        onChange={handleStatusFilterChange}
        value="soldOut"
      />
      <RadioInput
        checked={status === 'expired'}
        label="Expirée"
        name="status"
        onChange={handleStatusFilterChange}
        value="expired"
      />
      <button
        className="primary-button"
        onClick={refreshOffers}
        type="button"
      >
        {'Appliquer'}
      </button>
    </div>
  )
}

OffersStatusFiltersModal.defaultProps = {
  status: null,
}

OffersStatusFiltersModal.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  refreshOffers: PropTypes.func.isRequired,
  setIsVisible: PropTypes.func.isRequired,
  status: PropTypes.string,
  updateStatusFilter: PropTypes.func.isRequired,
}

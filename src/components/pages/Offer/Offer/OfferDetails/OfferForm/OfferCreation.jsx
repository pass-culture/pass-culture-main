import PropTypes from 'prop-types'
import React, { useEffect, useRef, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'

import OfferForm from './OfferForm'

const OfferCreation = ({
  initialValues,
  isLoading,
  isUserAdmin,
  onSubmit,
  showErrorNotification,
  setIsLoading,
  setShowThumbnailForm,
  submitErrors,
}) => {
  const venues = useRef([])
  const [displayedVenues, setDisplayedVenues] = useState([])
  const types = useRef([])
  const offerers = useRef([])
  const [selectedOfferer, setSelectedOfferer] = useState(initialValues.offererId)

  useEffect(
    function retrieveDataOnMount() {
      const requests = []
      const typesRequest = pcapi.loadTypes().then(receivedTypes => (types.current = receivedTypes))
      const offerersRequest = pcapi.getValidatedOfferers().then(receivedOfferers => {
        offerers.current = receivedOfferers
        if (receivedOfferers.length === 1) {
          initialValues.offererId = receivedOfferers[0].id
        }
      })
      if (!isUserAdmin) {
        const venuesRequest = pcapi.getVenuesForOfferer().then(receivedVenues => {
          venues.current = receivedVenues
          setDisplayedVenues(receivedVenues)

          if (receivedVenues.length === 1) {
            initialValues.venueId = receivedVenues[0].id
          }
        })
        requests.push(venuesRequest)
      }
      requests.push([typesRequest, offerersRequest])
      Promise.all(requests).then(() => setIsLoading(false))
    },
    [initialValues, isUserAdmin, setIsLoading]
  )
  useEffect(
    function filterVenuesOfOfferer() {
      if (isUserAdmin && selectedOfferer) {
        pcapi
          .getVenuesForOfferer(selectedOfferer)
          .then(receivedVenues => setDisplayedVenues(receivedVenues))
      } else if (!isUserAdmin) {
        const venuesToDisplay = selectedOfferer
          ? venues.current.filter(venue => venue.managingOffererId === selectedOfferer)
          : venues.current
        setDisplayedVenues(venuesToDisplay)
      }
    },
    [isUserAdmin, selectedOfferer]
  )

  if (isLoading) {
    return null
  }

  return (
    <OfferForm
      initialValues={initialValues}
      isUserAdmin={isUserAdmin}
      offerers={offerers.current}
      onSubmit={onSubmit}
      setIsLoading={setIsLoading}
      setSelectedOfferer={setSelectedOfferer}
      setShowThumbnailForm={setShowThumbnailForm}
      showErrorNotification={showErrorNotification}
      submitErrors={submitErrors}
      types={types.current}
      venues={displayedVenues}
    />
  )
}

OfferCreation.defaultProps = {
  initialValues: {},
  isUserAdmin: false,
}

OfferCreation.propTypes = {
  initialValues: PropTypes.shape(),
  isLoading: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  setIsLoading: PropTypes.func.isRequired,
  setShowThumbnailForm: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
}

export default OfferCreation

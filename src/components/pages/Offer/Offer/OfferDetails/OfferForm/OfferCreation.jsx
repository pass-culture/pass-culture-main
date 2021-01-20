import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef, useState } from 'react'

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
  const types = useRef([])
  const offerers = useRef([])
  const [displayedVenues, setDisplayedVenues] = useState([])
  const [selectedOfferer, setSelectedOfferer] = useState(initialValues.offererId)

  useEffect(() => setSelectedOfferer(initialValues.offererId), [initialValues.offererId])
  useEffect(
    function retrieveDataOnMount() {
      const typesRequest = pcapi.loadTypes().then(receivedTypes => (types.current = receivedTypes))
      const offerersRequest = pcapi.getValidatedOfferers().then(receivedOfferers => {
        offerers.current = receivedOfferers
      })
      const requests = [typesRequest, offerersRequest]
      if (!isUserAdmin) {
        const venuesRequest = pcapi.getVenuesForOfferer().then(receivedVenues => {
          venues.current = receivedVenues
          const venuesToDisplay = initialValues.offererId
            ? receivedVenues.filter(venue => venue.managingOffererId === initialValues.offererId)
            : receivedVenues
          setDisplayedVenues(venuesToDisplay)
        })
        requests.push(venuesRequest)
      }
      Promise.all(requests).then(() => setIsLoading(false))
    },
    [initialValues.offererId, isUserAdmin, setIsLoading]
  )

  const getVenuesForAdmin = useCallback(() => {
    if (selectedOfferer) {
      pcapi
        .getVenuesForOfferer(selectedOfferer)
        .then(receivedVenues => setDisplayedVenues(receivedVenues))
    } else {
      setDisplayedVenues([])
    }
  }, [selectedOfferer])

  const filterVenuesForPro = useCallback(() => {
    const venuesToDisplay = selectedOfferer
      ? venues.current.filter(venue => venue.managingOffererId === selectedOfferer)
      : venues.current
    setDisplayedVenues(venuesToDisplay)
  }, [selectedOfferer])

  useEffect(() => {
    if (isUserAdmin) {
      getVenuesForAdmin()
    } else {
      filterVenuesForPro()
    }
  }, [filterVenuesForPro, getVenuesForAdmin, isUserAdmin])

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

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferForm from './OfferForm'

const OfferCreation = ({
  formValues,
  initialValues,
  isUserAdmin,
  userEmail,
  onSubmit,
  showErrorNotification,
  setPreviewOfferType,
  setShowThumbnailForm,
  setFormValues,
  submitErrors,
}) => {
  const venues = useRef([])
  const types = useRef([])
  const offerersNames = useRef([])
  const [isLoading, setIsLoading] = useState(true)
  const [displayedVenues, setDisplayedVenues] = useState([])
  const [selectedOfferer, setSelectedOfferer] = useState(initialValues.offererId)

  useEffect(() => setSelectedOfferer(initialValues.offererId), [initialValues.offererId])
  useEffect(
    function retrieveDataOnMount() {
      const typesRequest = pcapi.loadTypes().then(receivedTypes => (types.current = receivedTypes))
      const requests = [typesRequest]
      if (isUserAdmin) {
        const offererRequest = pcapi.getOfferer(initialValues.offererId).then(receivedOfferer => {
          offerersNames.current = [
            {
              id: receivedOfferer.id,
              name: receivedOfferer.name,
            },
          ]
          venues.current = receivedOfferer.managedVenues
          setDisplayedVenues(receivedOfferer.managedVenues)
        })
        requests.push(offererRequest)
      } else {
        const offerersRequest = pcapi.getUserValidatedOfferersNames().then(receivedOfferers => {
          offerersNames.current = receivedOfferers
        })
        const venuesRequest = pcapi
          .getVenuesForOfferer({ activeOfferersOnly: true })
          .then(receivedVenues => {
            venues.current = receivedVenues
            const venuesToDisplay = initialValues.offererId
              ? receivedVenues.filter(venue => venue.managingOffererId === initialValues.offererId)
              : receivedVenues
            setDisplayedVenues(venuesToDisplay)
          })
        requests.push(offerersRequest, venuesRequest)
      }
      Promise.all(requests).then(() => setIsLoading(false))
    },
    [initialValues.offererId, isUserAdmin, setIsLoading]
  )

  const filterVenuesForPro = useCallback(() => {
    const venuesToDisplay = selectedOfferer
      ? venues.current.filter(venue => venue.managingOffererId === selectedOfferer)
      : venues.current
    setDisplayedVenues(venuesToDisplay)
  }, [selectedOfferer])

  useEffect(() => {
    if (!isUserAdmin) {
      filterVenuesForPro()
    }
  }, [filterVenuesForPro, isUserAdmin])

  const isComingFromOffererPage = initialValues.offererId !== undefined

  const areAllVenuesVirtual =
    isComingFromOffererPage && selectedOfferer === initialValues.offererId
      ? venues.current
          .filter(venue => venue.managingOffererId === selectedOfferer)
          .every(venue => venue.isVirtual)
      : venues.current.every(venue => venue.isVirtual)

  if (isLoading) {
    return <Spinner />
  }

  return (
    <OfferForm
      areAllVenuesVirtual={areAllVenuesVirtual}
      formValues={formValues}
      initialValues={initialValues}
      isUserAdmin={isUserAdmin}
      offerersNames={offerersNames.current}
      onSubmit={onSubmit}
      readOnlyFields={isUserAdmin ? ['offererId'] : []}
      setFormValues={setFormValues}
      setIsLoading={setIsLoading}
      setPreviewOfferType={setPreviewOfferType}
      setSelectedOfferer={setSelectedOfferer}
      setShowThumbnailForm={setShowThumbnailForm}
      showErrorNotification={showErrorNotification}
      submitErrors={submitErrors}
      types={types.current}
      userEmail={userEmail}
      venues={displayedVenues}
    />
  )
}

OfferCreation.defaultProps = {
  initialValues: {},
  isUserAdmin: false,
}

OfferCreation.propTypes = {
  formValues: PropTypes.shape().isRequired,
  initialValues: PropTypes.shape(),
  isUserAdmin: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  setFormValues: PropTypes.func.isRequired,
  setPreviewOfferType: PropTypes.func.isRequired,
  setShowThumbnailForm: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferCreation

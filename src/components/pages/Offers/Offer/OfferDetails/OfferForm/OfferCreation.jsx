/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferForm from './OfferForm'

const OfferCreation = ({
  formValues,
  initialValues,
  isSubmitLoading,
  isUserAdmin,
  userEmail,
  onSubmit,
  showErrorNotification,
  setPreviewOfferCategory,
  setFormValues,
  submitErrors,
}) => {
  const venues = useRef([])
  const offerersNames = useRef([])
  const [isLoading, setIsLoading] = useState(true)
  const [displayedVenues, setDisplayedVenues] = useState([])
  const [selectedOfferer, setSelectedOfferer] = useState(initialValues.offererId)

  const { categories } = useSelector(state => state.offers.categories)

  useEffect(() => setSelectedOfferer(initialValues.offererId), [initialValues.offererId])

  useEffect(() => {
    (async () => {
      // On first load store.offers.categories is not set.
      // in this case we want do display the spinner using isLoading === true.
      if (categories === undefined) {
        return
      }

      if (isUserAdmin) {
        const offererResponse = await pcapi.getOfferer(initialValues.offererId)

        offerersNames.current = [
          {
            id: offererResponse.id,
            name: offererResponse.name,
          },
        ]
        venues.current = offererResponse.managedVenues
        setDisplayedVenues(offererResponse.managedVenues)
      } else {
        const offerersResponse = await pcapi.getUserValidatedOfferersNames()
        offerersNames.current = offerersResponse

        const venuesResponse = await pcapi.getVenuesForOfferer({ activeOfferersOnly: true })
        venues.current = venuesResponse

        const venuesToDisplay = initialValues.offererId
          ? venuesResponse.filter(venue => venue.managingOffererId === initialValues.offererId)
          : venuesResponse

        setDisplayedVenues(venuesToDisplay)
      }

      setIsLoading(false)
    })()
  }, [initialValues.offererId, isUserAdmin, initialValues, categories])

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
      backUrl={computeOffersUrl({})}
      formValues={formValues}
      initialValues={initialValues}
      isSubmitLoading={isSubmitLoading}
      isUserAdmin={isUserAdmin}
      offerersNames={offerersNames.current}
      onSubmit={onSubmit}
      readOnlyFields={isUserAdmin ? ['offererId'] : []}
      setFormValues={setFormValues}
      setIsLoading={setIsLoading}
      setPreviewOfferCategory={setPreviewOfferCategory}
      setSelectedOfferer={setSelectedOfferer}
      showErrorNotification={showErrorNotification}
      submitErrors={submitErrors}
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
  isSubmitLoading: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  setFormValues: PropTypes.func.isRequired,
  setPreviewOfferCategory: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferCreation

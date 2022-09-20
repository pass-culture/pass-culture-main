import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'core/Offers/utils'
import getUserValidatedOfferersNamesAdapter from 'core/shared/adapters/getUserValidatedOfferersNamesAdapter'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferForm from '../OfferForm'

const OfferCreation = ({
  categories,
  initialValues,
  isUserAdmin,
  setOfferPreviewData,
  userEmail,
  onSubmit,
  showErrorNotification,
  subCategories,
  submitErrors,
}) => {
  const venues = useRef([])
  const offerersNames = useRef([])
  const [isLoading, setIsLoading] = useState(true)
  const [displayedVenues, setDisplayedVenues] = useState([])
  const [selectedOfferer, setSelectedOfferer] = useState(
    initialValues.offererId
  )

  useEffect(
    () => setSelectedOfferer(initialValues.offererId),
    [initialValues.offererId]
  )

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-extra-semi
    ;(async () => {
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
        const offerersResponse = await getUserValidatedOfferersNamesAdapter()
        offerersNames.current = offerersResponse.payload

        const venuesResponse = await pcapi.getVenuesForOfferer({
          activeOfferersOnly: true,
        })
        venues.current = venuesResponse

        const venuesToDisplay = initialValues.offererId
          ? venuesResponse.filter(
              venue => venue.managingOffererId === initialValues.offererId
            )
          : venuesResponse

        setDisplayedVenues(venuesToDisplay)
      }

      setIsLoading(false)
    })()
  }, [initialValues.offererId, isUserAdmin, initialValues])

  const filterVenuesForPro = useCallback(() => {
    const venuesToDisplay = selectedOfferer
      ? venues.current.filter(
          venue => venue.managingOffererId === selectedOfferer
        )
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
      categories={categories}
      initialValues={initialValues}
      isUserAdmin={isUserAdmin}
      offerersNames={offerersNames.current}
      onSubmit={onSubmit}
      readOnlyFields={isUserAdmin ? ['offererId'] : []}
      setIsLoading={setIsLoading}
      setOfferPreviewData={setOfferPreviewData}
      setSelectedOfferer={setSelectedOfferer}
      showErrorNotification={showErrorNotification}
      subCategories={subCategories}
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
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  initialValues: PropTypes.shape(),
  isUserAdmin: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  setOfferPreviewData: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferCreation

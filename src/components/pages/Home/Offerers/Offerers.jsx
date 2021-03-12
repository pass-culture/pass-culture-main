import React, { useCallback, useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import { VenueList } from 'components/pages/Home/Venues/VenueList'
import * as pcapi from 'repository/pcapi/pcapi'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

import CreationLinks from './CreationLinks'
import OffererDetails from './OffererDetails'

export const CREATE_OFFERER_SELECT_ID = 'creation'

const Offerers = () => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState([])
  const [virtualVenue, setVirtualVenue] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)

  const history = useHistory()

  useEffect(function fetchData() {
    pcapi.getAllOfferersNames().then(receivedOffererNames => {
      setSelectedOffererId(receivedOffererNames[0].id)
      setOffererOptions([
        ...buildSelectOptions('id', 'name', receivedOffererNames),
        {
          displayName: '+ Ajouter une structure',
          id: CREATE_OFFERER_SELECT_ID,
        },
      ])
    })
  }, [])

  useEffect(() => {
    if (!selectedOffererId) return
    pcapi
      .getOfferer(selectedOffererId)
      .then(receivedOfferer => {
        setSelectedOfferer(receivedOfferer)
        setPhysicalVenues(receivedOfferer.managedVenues.filter(venue => !venue.isVirtual))
        const virtualVenue = receivedOfferer.managedVenues.find(venue => venue.isVirtual)
        setVirtualVenue(virtualVenue)
        setIsUserOffererValidated(true)
      })
      .catch(error => {
        if (error.status === HTTP_STATUS.FORBIDDEN) {
          setSelectedOfferer({ id: selectedOffererId })
          setIsUserOffererValidated(false)
        }
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [setIsLoading, selectedOffererId])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId === CREATE_OFFERER_SELECT_ID) {
        history.push('/structures/creation')
      } else if (newOffererId !== selectedOfferer.id) {
        setSelectedOffererId(newOffererId)
      }
    },
    [history, selectedOfferer, setSelectedOffererId]
  )

  if (isLoading) {
    return (
      <div className="h-card h-card-secondary h-card-placeholder">
        <div className="h-card-inner">
          <Spinner />
        </div>
      </div>
    )
  }

  return (
    <>
      <OffererDetails
        handleChangeOfferer={handleChangeOfferer}
        hasPhysicalVenues={physicalVenues.length > 0}
        isUserOffererValidated={isUserOffererValidated}
        offererOptions={offererOptions}
        selectedOfferer={selectedOfferer}
      />

      <VenueList
        physicalVenues={physicalVenues}
        selectedOffererId={selectedOfferer.id}
        virtualVenue={virtualVenue?.nOffers ? virtualVenue : null}
      />

      {isUserOffererValidated && (
        <CreationLinks
          hasPhysicalVenue={physicalVenues.length > 0}
          hasVirtualOffers={virtualVenue?.nOffers > 0}
          offererId={selectedOfferer.id}
        />
      )}
    </>
  )
}

export default Offerers

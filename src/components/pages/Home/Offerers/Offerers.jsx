import React, { useCallback, useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import {
  INITIAL_PHYSICAL_VENUES,
  INITIAL_VIRTUAL_VENUE,
} from 'components/pages/Home/Offerers/_constants'
import { VenueList } from 'components/pages/Home/Venues/VenueList'
import * as pcapi from 'repository/pcapi/pcapi'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

import OffererCreationLinks from './OffererCreationLinks'
import OffererDetails from './OffererDetails'
import VenueCreationLinks from './VenueCreationLinks'

export const CREATE_OFFERER_SELECT_ID = 'creation'

const Offerers = () => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState(INITIAL_PHYSICAL_VENUES)
  const [virtualVenue, setVirtualVenue] = useState(INITIAL_VIRTUAL_VENUE)
  const [isLoading, setIsLoading] = useState(true)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)

  const history = useHistory()

  useEffect(function fetchData() {
    pcapi.getAllOfferersNames().then(receivedOffererNames => {
      if (receivedOffererNames.length > 0) {
        setSelectedOffererId(receivedOffererNames[0].id)
      }
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
    if (selectedOffererId) {
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
            setSelectedOfferer({ id: selectedOffererId, managedVenues: [] })
            setPhysicalVenues(INITIAL_PHYSICAL_VENUES)
            setVirtualVenue(INITIAL_VIRTUAL_VENUE)
            setIsUserOffererValidated(false)
          }
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsLoading(false)
    }
  }, [selectedOffererId])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId === CREATE_OFFERER_SELECT_ID) {
        history.push('/structures/creation')
      } else if (newOffererId !== selectedOfferer.id) {
        setSelectedOffererId(newOffererId)
      }
    },
    [history, selectedOfferer]
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
      {selectedOfferer && (
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
        </>
      )}

      {selectedOffererId === null && <OffererCreationLinks />}

      {isUserOffererValidated && (
        <VenueCreationLinks
          hasPhysicalVenue={physicalVenues.length > 0}
          hasVirtualOffers={virtualVenue && virtualVenue.nOffers > 0}
          offererId={selectedOfferer ? selectedOfferer.id : null}
        />
      )}
    </>
  )
}

export default Offerers

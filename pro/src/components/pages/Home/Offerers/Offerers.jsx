/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React, { useCallback, useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import useFrenchQuery from 'components/hooks/useFrenchQuery'
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
  const [query, setQuery] = useFrenchQuery()

  useEffect(
    function fetchData() {
      const { offererId } = query
      pcapi.getAllOfferersNames().then(receivedOffererNames => {
        const initialOffererOptions = buildSelectOptions('id', 'name', receivedOffererNames)
        if (initialOffererOptions.length > 0) {
          setSelectedOffererId(offererId || initialOffererOptions[0].id)
          setOffererOptions([
            ...initialOffererOptions,
            {
              displayName: '+ Ajouter une structure',
              id: CREATE_OFFERER_SELECT_ID,
            },
          ])
        } else {
          setIsLoading(false)
        }
      })
    },
    [query]
  )

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
          setSelectedOfferer({ id: selectedOffererId, managedVenues: [] })
          setPhysicalVenues(INITIAL_PHYSICAL_VENUES)
          setVirtualVenue(INITIAL_VIRTUAL_VENUE)
          setIsUserOffererValidated(false)
        }
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [selectedOffererId])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId === CREATE_OFFERER_SELECT_ID) {
        history.push('/structures/creation')
      } else if (newOffererId !== selectedOfferer.id) {
        setSelectedOffererId(newOffererId)
        setQuery({ offererId: newOffererId })
      }
    },
    [history, selectedOfferer, setQuery]
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

  const userHasOfferers = offererOptions.length > 0
  return (
    <>
      {userHasOfferers && selectedOfferer && (
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
            virtualVenue={selectedOfferer.hasDigitalVenueAtLeastOneOffer ? virtualVenue : null}
          />
        </>
      )}

      {!userHasOfferers && <OffererCreationLinks />}

      {isUserOffererValidated && (
        <VenueCreationLinks
          hasPhysicalVenue={physicalVenues.length > 0}
          hasVirtualOffers={!!virtualVenue && !!selectedOfferer.hasDigitalVenueAtLeastOneOffer}
          offererId={selectedOfferer ? selectedOfferer.id : null}
        />
      )}
    </>
  )
}

export default Offerers

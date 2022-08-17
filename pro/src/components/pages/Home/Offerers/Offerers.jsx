import React, { useCallback, useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import useFrenchQuery from 'components/hooks/useFrenchQuery'
import Spinner from 'components/layout/Spinner'
import {
  INITIAL_PHYSICAL_VENUES,
  INITIAL_VIRTUAL_VENUE,
} from 'components/pages/Home/Offerers/_constants'
import { VenueList } from 'components/pages/Home/Venues/VenueList'
import SoftDeletedOffererWarning from 'new_components/SoftDeletedOffererWarning'
import * as pcapi from 'repository/pcapi/pcapi'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { sortByDisplayName } from 'utils/strings'

import OffererCreationLinks from './OffererCreationLinks'
import OffererDetails from './OffererDetails'
import VenueCreationLinks from './VenueCreationLinks'

export const CREATE_OFFERER_SELECT_ID = 'creation'

const Offerers = ({ setVenues }) => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [businessUnitList, setBusinessUnitList] = useState([])
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
        const initialOffererOptions = sortByDisplayName(
          receivedOffererNames.map(item => ({
            id: item['id'].toString(),
            displayName: item['name'],
          }))
        )

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
    async function loadOfferer(offererId) {
      try {
        const receivedOfferer = await pcapi.getOfferer(offererId)
        setSelectedOfferer(receivedOfferer)
        setPhysicalVenues(
          receivedOfferer.managedVenues.filter(venue => !venue.isVirtual)
        )
        setVenues(
          receivedOfferer.managedVenues.filter(venue => !venue.isVirtual)
        )
        const virtualVenue = receivedOfferer.managedVenues.find(
          venue => venue.isVirtual
        )
        setVirtualVenue(virtualVenue)
        setIsUserOffererValidated(true)

        const receivedBusinessUnitList = await pcapi.getBusinessUnits(offererId)
        setBusinessUnitList(receivedBusinessUnitList)
      } catch (error) {
        if (error.status === HTTP_STATUS.FORBIDDEN) {
          setSelectedOfferer({ id: offererId, managedVenues: [] })
          setBusinessUnitList([])
          setPhysicalVenues(INITIAL_PHYSICAL_VENUES)
          setVirtualVenue(INITIAL_VIRTUAL_VENUE)
          setIsUserOffererValidated(false)
        }
      }
      setIsLoading(false)
    }
    selectedOffererId && loadOfferer(selectedOffererId)
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

  const isOffererSoftDeleted =
    selectedOfferer && selectedOfferer.isActive === false
  const userHasOfferers = offererOptions.length > 0
  return (
    <>
      {userHasOfferers && selectedOfferer && (
        <>
          <OffererDetails
            businessUnitList={businessUnitList}
            handleChangeOfferer={handleChangeOfferer}
            hasPhysicalVenues={physicalVenues.length > 0}
            isUserOffererValidated={isUserOffererValidated}
            offererOptions={offererOptions}
            selectedOfferer={selectedOfferer}
          />

          {!isOffererSoftDeleted && (
            <VenueList
              physicalVenues={physicalVenues}
              selectedOffererId={selectedOfferer.id}
              virtualVenue={
                selectedOfferer.hasDigitalVenueAtLeastOneOffer
                  ? virtualVenue
                  : null
              }
            />
          )}
        </>
      )}

      {isOffererSoftDeleted && <SoftDeletedOffererWarning />}

      {!userHasOfferers && <OffererCreationLinks />}

      {isUserOffererValidated && !isOffererSoftDeleted && (
        <VenueCreationLinks
          hasPhysicalVenue={physicalVenues.length > 0}
          hasVirtualOffers={
            !!virtualVenue && !!selectedOfferer.hasDigitalVenueAtLeastOneOffer
          }
          offererId={selectedOfferer ? selectedOfferer.id : null}
        />
      )}
    </>
  )
}

export default Offerers

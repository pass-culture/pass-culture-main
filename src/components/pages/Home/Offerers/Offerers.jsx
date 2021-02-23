import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useHistory } from 'react-router-dom'

import { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import { VenueList } from 'components/pages/Home/Venues/VenueList'
import * as pcapi from 'repository/pcapi/pcapi'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import OffererDetails from './OffererDetails'

export const CREATE_OFFERER_SELECT_ID = 'creation'


const Offerers = ({ isVenueCreationAvailable }) => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState([])
  const [virtualVenue, setVirtualVenue] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

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
    pcapi.getOfferer(selectedOffererId).then(receivedOfferer => {
      setSelectedOfferer(receivedOfferer)
      setPhysicalVenues(receivedOfferer.managedVenues.filter(venue => !venue.isVirtual))
      const virtualVenue = receivedOfferer.managedVenues.find(
        venue => venue.isVirtual && venue.nOffers > 0
      )
      setVirtualVenue(virtualVenue || null)
      setIsLoading(false)
    })
  }, [setIsLoading, selectedOffererId])

  const displayCreateVenueBanner = useMemo(() => {
    if (!selectedOfferer) return false
    const virtualVenue = selectedOfferer.managedVenues.find(venue => venue.isVirtual)
    return !physicalVenues.length && !virtualVenue.nOffers
  }, [selectedOfferer, physicalVenues])

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

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${selectedOffererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <>
      <OffererDetails
        handleChangeOfferer={handleChangeOfferer}
        hasPhysicalVenues={physicalVenues.length > 0}
        offererOptions={offererOptions}
        selectedOfferer={selectedOfferer}
      />

      {displayCreateVenueBanner ? (
        <div className="h-card venue-banner">
          <div className="h-card-inner">
            <h3 className="h-card-title">
              {'Lieux'}
            </h3>

            <div className="h-card-content">
              <p>
                {'Avant de créer votre première offre physique vous devez avoir un lieu'}
              </p>
              <div className="actions-container">
                <Link
                  className="primary-link"
                  to={venueCreationUrl}
                >
                  {'Créer un lieu'}
                </Link>
                <Link
                  className="secondary-link"
                  to={`/offres/creation?structure=${selectedOfferer.id}`}
                >
                  {'Créer une offre numérique'}
                </Link>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <VenueList
          physicalVenues={physicalVenues}
          selectedOffererId={selectedOfferer.id}
          virtualVenue={virtualVenue}
        />
      )}
    </>
  )
}

Offerers.propTypes = {
  isVenueCreationAvailable: PropTypes.bool.isRequired,
}

export default Offerers

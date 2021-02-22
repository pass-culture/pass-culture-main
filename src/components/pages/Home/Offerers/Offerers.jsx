import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import OffererDetails from './OffererDetails'

const Offerers = ({ isVenueCreationAvailable }) => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(function fetchData() {
    pcapi.getAllOfferersNames().then(receivedOffererNames => {
      setSelectedOffererId(receivedOffererNames[0].id)
      setOffererOptions(buildSelectOptions('id', 'name', receivedOffererNames))
    })
  }, [])

  useEffect(() => {
    if (!selectedOffererId) return
    pcapi.getOfferer(selectedOffererId).then(receivedOfferer => {
      setSelectedOfferer(receivedOfferer)
      setPhysicalVenues(receivedOfferer.managedVenues.filter(venue => !venue.isVirtual))
      setIsLoading(false)
    })
  }, [setIsLoading, selectedOffererId, setSelectedOfferer])

  const displayCreateVenueBanner = useMemo(() => {
    if (!selectedOfferer) return false
    const virtualVenue = selectedOfferer.managedVenues.find(venue => venue.isVirtual)
    return !physicalVenues.length && !virtualVenue.nOffers
  }, [selectedOfferer, physicalVenues])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId !== selectedOfferer.id) {
        setSelectedOffererId(newOffererId)
      }
    },
    [selectedOfferer, setSelectedOffererId]
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
        <div className="h-venue-list">
          <div className="h-section-row nested">
            <div className="h-card h-card-primary">
              <div className="h-card-inner">
                <h3 className="h-card-title">
                  <Icon
                    className="h-card-title-ico"
                    svg="ico-screen-play"
                  />
                  {'Lieu numérique'}
                </h3>
              </div>
            </div>
          </div>

          {physicalVenues &&
            physicalVenues.map(venue => (
              <div
                className="h-section-row nested"
                key={venue.id}
              >
                <div className="h-card h-card-secondary">
                  <div className="h-card-inner">
                    <div className="h-card-header-row">
                      <h3 className="h-card-title">
                        <Icon
                          className="h-card-title-ico"
                          svg="ico-box"
                        />
                        {venue.publicName || venue.name}
                      </h3>
                      <Link
                        className="tertiary-link"
                        to={`/structures/${selectedOfferer.id}/lieux/${venue.id}`}
                      >
                        <Icon svg="ico-outer-pen" />
                        {'Modifier'}
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </>
  )
}

Offerers.propTypes = {
  isVenueCreationAvailable: PropTypes.bool.isRequired,
}

export default Offerers

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import { DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { steps, STEP_ID_OFFERERS } from '../HomepageBreadcrumb'

const Offerers = ({ isVenueCreationAvailable }) => {
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOffererId, setSelectedOffererId] = useState(null)
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [offlineVenues, setOfflineVenues] = useState([])
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
      setOfflineVenues(receivedOfferer.managedVenues.filter(venue => !venue.isVirtual))
      setIsLoading(false)
    })
  }, [setIsLoading, selectedOffererId, setSelectedOfferer])

  const displayCreateVenueBanner = useMemo(() => {
    if (!selectedOfferer) return false
    const virtualVenue = selectedOfferer.managedVenues.find(venue => venue.isVirtual)
    return !offlineVenues.length && !virtualVenue.nOffers
  }, [selectedOfferer, offlineVenues])

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

  const hasAccountData = selectedOfferer.iban && selectedOfferer.bic
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${selectedOffererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <>
      <div className="h-card h-card-secondary">
        <div className="h-card-inner">
          <div className="h-card-header">
            <div className="h-card-header-block">
              <Select
                handleSelection={handleChangeOfferer}
                id={steps[STEP_ID_OFFERERS].hash}
                name="offererId"
                options={offererOptions}
                selectedValue={selectedOfferer.id}
              />
            </div>
            <div className="h-card-actions">
              <Link
                className="tertiary-link"
                to={`/structures/${selectedOfferer.id}`}
              >
                <Icon svg="ico-outer-pen" />
                {'Modifier'}
              </Link>
            </div>
          </div>
          <div className="h-card-cols">
            <div className="h-card-col">
              <h3 className="h-card-secondary-title">
                {'Informations pratiques'}
              </h3>
              <div className="h-card-content">
                <ul className="h-description-list">
                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Siren :'}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.siren}
                    </span>
                  </li>

                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Désignation :'}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.name}
                    </span>
                  </li>

                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Siège social : '}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.address} 
                      {' '}
                      {selectedOfferer.postalCode} 
                      {' '}
                      {selectedOfferer.city}
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="h-card-col">
              <h3 className="h-card-secondary-title">
                {'Coordonnées bancaires'}
              </h3>

              <div className="h-card-content">
                {hasAccountData ? (
                  <>
                    <p>
                      {
                        'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres.'
                      }
                    </p>
                    <ul className="h-description-list">
                      <li className="h-dl-row">
                        <span className="h-dl-title">
                          {'IBAN :'}
                        </span>
                        <span className="h-dl-description">
                          {selectedOfferer.iban}
                        </span>
                      </li>

                      <li className="h-dl-row">
                        <span className="h-dl-title">
                          {'BIC :'}
                        </span>
                        <span className="h-dl-description">
                          {selectedOfferer.bic}
                        </span>
                      </li>
                    </ul>
                  </>
                ) : selectedOfferer.demarchesSimplifieesApplicationId ? (
                  <Banner
                    href={`https://www.demarches-simplifiees.fr/dossiers/${selectedOfferer.demarchesSimplifieesApplicationId}`}
                    linkTitle="Voir le dossier"
                    subtitle="Votre dossier est en cours pour cette structure"
                  />
                ) : (
                  <Banner
                    href={DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL}
                    linkTitle="Renseignez les coordonnées bancaires de la structure"
                    subtitle="Renseignez vos coordonnées bancaires pour être remboursé de vos offres éligibles"
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

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
          {offlineVenues &&
            offlineVenues.map(venue => (
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

import './VenueProvidersManager.scss'

import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import AddVenueProviderButton from './AddVenueProviderButton'
import VenueProviderList from './VenueProviderList'

const VenueProvidersManager = ({ venue }) => {
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      const providersResponse = await pcapi.loadProviders(venue.id)
      setProviders(providersResponse)

      const venueProvidersResponse = await pcapi.loadVenueProviders(venue.id)
      setVenueProviders(venueProvidersResponse)
      setIsLoading(false)
    }
    fetchData()
  }, [venue.id])

  const afterVenueProviderEdit = ({ editedVenueProvider }) => {
    const newVenueProviders = venueProviders.map(venueProvider =>
      venueProvider.id === editedVenueProvider.id
        ? editedVenueProvider
        : venueProvider
    )
    setVenueProviders(newVenueProviders)
  }

  if (!isLoading && !providers.length && !venueProviders.length) {
    return null
  }

  return (
    <div className="venue-providers-manager section">
      <h2 className="main-list-title">Importation d’offres</h2>

      {isLoading ? (
        <Spinner />
      ) : venueProviders.length > 0 ? (
        <VenueProviderList
          afterVenueProviderEdit={afterVenueProviderEdit}
          venue={venue}
          venueProviders={venueProviders}
        />
      ) : (
        <AddVenueProviderButton
          providers={providers}
          setVenueProviders={setVenueProviders}
          venue={venue}
        />
      )}
    </div>
  )
}

VenueProvidersManager.propTypes = {
  venue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    managingOffererId: PropTypes.string.isRequired,
    siret: PropTypes.string,
    departementCode: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueProvidersManager

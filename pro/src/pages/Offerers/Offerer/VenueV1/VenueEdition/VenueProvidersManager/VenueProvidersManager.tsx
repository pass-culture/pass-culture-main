import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import { IVenue } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import Spinner from 'ui-kit/Spinner/Spinner'

import AddVenueProviderButton from './AddVenueProviderButton'
import VenueProviderList from './VenueProviderList/VenueProviderList'
import styles from './VenueProvidersManager.module.scss'
import VenueProviderStatus from './VenueProviderStatus/VenueProviderStatus'

interface VenueProvidersManagerV2Props {
  venue: IVenue
}

const VenueProvidersManager = ({
  venue,
}: VenueProvidersManagerV2Props): JSX.Element | null => {
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState<VenueProviderResponse[]>(
    []
  )
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      const providersResponse = await pcapi.loadProviders(venue.nonHumanizedId)
      setProviders(providersResponse)

      const venueProvidersResponse = await api.listVenueProviders(
        venue.nonHumanizedId
      )
      setVenueProviders(venueProvidersResponse.venue_providers)
      setIsLoading(false)
    }
    fetchData()
  }, [venue.nonHumanizedId])

  const afterVenueProviderEdit = (
    editedVenueProvider: VenueProviderResponse
  ) => {
    const newVenueProviders = venueProviders.map(venueProvider =>
      venueProvider.id === editedVenueProvider.id
        ? editedVenueProvider
        : venueProvider
    )
    setVenueProviders(newVenueProviders)
  }

  const afterVenueProviderDelete = (deletedVenueProviderId: number) => {
    const newVenueProviders = venueProviders.filter(
      venueProvider => venueProvider.id !== deletedVenueProviderId
    )
    setVenueProviders(newVenueProviders)
  }

  if (!isLoading && !providers.length && !venueProviders.length) {
    return null
  }

  const isSynchronizationActive =
    venueProviders.filter(venueProvider => venueProvider.isActive).length != 0

  return (
    <div className={`${styles['venue-providers-manager']} section`}>
      <div className={styles['main-list-title']}>
        <h2 className={styles['main-list-title-text']}>
          Synchronisation des offres
        </h2>
        {!!venueProviders.length && (
          <VenueProviderStatus isActive={isSynchronizationActive} />
        )}
      </div>

      {isLoading ? (
        <Spinner />
      ) : venueProviders.length > 0 ? (
        <VenueProviderList
          afterVenueProviderDelete={afterVenueProviderDelete}
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

export default VenueProvidersManager

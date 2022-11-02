import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import { IVenue } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import Spinner from 'ui-kit/Spinner/Spinner'

import AddVenueProviderButton from '../VenueProvidersManager/AddVenueProviderButton'

import VenueProviderListV2 from './VenueProviderListV2/VenueProviderListV2'
import styles from './VenueProvidersManagerV2.module.scss'
import VenueProviderStatus from './VenueProviderStatus/VenueProviderStatus'

export interface IVenueProvidersManagerV2Props {
  venue: IVenue
}

const VenueProvidersManagerV2 = ({
  venue,
}: IVenueProvidersManagerV2Props): JSX.Element | null => {
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState<VenueProviderResponse[]>(
    []
  )
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      const providersResponse = await pcapi.loadProviders(venue.id)
      setProviders(providersResponse)

      // @ts-expect-error string is not assignable to type number
      const venueProvidersResponse = await api.listVenueProviders(venue.id)
      setVenueProviders(venueProvidersResponse.venue_providers)
      setIsLoading(false)
    }
    fetchData()
  }, [venue.id])

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

  const afterVenueProviderDelete = (deletedVenueProviderId: string) => {
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
        <VenueProviderListV2
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

export default VenueProvidersManagerV2

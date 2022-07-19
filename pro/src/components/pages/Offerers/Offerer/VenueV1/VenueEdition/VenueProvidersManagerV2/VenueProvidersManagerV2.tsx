import * as pcapi from 'repository/pcapi/pcapi'
import React, { useEffect, useState } from 'react'
import AddVenueProviderButton from '../VenueProvidersManager/AddVenueProviderButton'
import { IAPIVenue } from 'core/Venue/types'
import { IVenueProviderApi } from '../VenueProvidersManager/CinemaProviderItem/types'
import Spinner from 'components/layout/Spinner'
import VenueProviderListV2 from './VenueProviderListV2/VenueProviderListV2'
import VenueProviderStatus from './VenueProviderStatus/VenueProviderStatus'
import styles from './VenueProvidersManagerV2.module.scss'

export interface IVenueProvidersManagerV2Props {
  venue: IAPIVenue
}

const VenueProvidersManagerV2 = ({
  venue,
}: IVenueProvidersManagerV2Props): JSX.Element | null => {
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState<IVenueProviderApi[]>([])
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

  const afterVenueProviderEdit = (editedVenueProvider: IVenueProviderApi) => {
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

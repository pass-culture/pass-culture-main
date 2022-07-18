import React, { useEffect, useState } from 'react'

import CollectiveDataForm from './CollectiveDataForm'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { GetCollectiveVenueResponseModel } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import Spinner from 'components/layout/Spinner'
import { Title } from 'ui-kit'
import { getCulturalPartnersAdapter } from '../adapters'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import getVenueCollectiveDataAdapter from './adapters/getVenueCollectiveDataAdapter'
import { getVenueEducationalStatusesAdapter } from './adapters'
import styles from './CollectiveDataEdition.module.scss'
import useNotification from 'components/hooks/useNotification'
import { useParams } from 'react-router-dom'

const CollectiveDataEdition = (): JSX.Element => {
  const notify = useNotification()
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()

  const [domains, setDomains] = useState<SelectOption[]>([])
  const [statuses, setStatuses] = useState<SelectOption[]>([])
  const [culturalPartners, setCulturalPartners] = useState<SelectOption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [venueCollectiveData, setVenueCollectiveData] =
    useState<GetCollectiveVenueResponseModel | null>(null)

  useEffect(() => {
    Promise.all([
      getEducationalDomainsAdapter(),
      getVenueEducationalStatusesAdapter(),
      getCulturalPartnersAdapter(),
      getVenueCollectiveDataAdapter(venueId),
    ]).then(
      ([
        domainsResponse,
        statusesResponse,
        culturalPartnersResponse,
        venueResponse,
      ]) => {
        if (
          [
            domainsResponse,
            statusesResponse,
            culturalPartnersResponse,
            venueResponse,
          ].some(response => !response.isOk)
        ) {
          notify.error(GET_DATA_ERROR_MESSAGE)
        }

        setDomains(domainsResponse.payload)
        setStatuses(statusesResponse.payload)
        setCulturalPartners(culturalPartnersResponse.payload)
        setVenueCollectiveData(venueResponse.payload)

        setIsLoading(false)
      }
    )
  }, [])

  return (
    <>
      <Title level={1}>Mes informations pour les enseignants</Title>
      <p className={styles.description}>
        Ce formulaire vous permet de renseigner des informations complémentaires
        concernant votre établissement et les actions menées auprès du public
        scolaire. Ces informations seront visibles par les enseignants et chefs
        d'établissement sur ADAGE. Cela leur permettra de mieux comprendre votre
        démarche d'éducation artistique et culturelle.
      </p>
      {isLoading ? (
        <Spinner className={styles.spinner} />
      ) : (
        <CollectiveDataForm
          statuses={statuses}
          domains={domains}
          culturalPartners={culturalPartners}
          venueId={venueId}
          offererId={offererId}
          venueCollectiveData={venueCollectiveData}
        />
      )}
    </>
  )
}

export default CollectiveDataEdition

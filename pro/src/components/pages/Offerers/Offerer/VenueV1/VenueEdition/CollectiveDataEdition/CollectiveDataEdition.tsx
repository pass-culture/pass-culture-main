import React, { useEffect, useState } from 'react'
import {
  getCulturalPartnersAdapter,
  getVenueEducationalStatusesAdapter,
} from './adapters'

import CollectiveDataForm from './CollectiveDataForm'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import Spinner from 'components/layout/Spinner'
import { Title } from 'ui-kit'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import styles from './CollectiveDataEdition.module.scss'
import useNotification from 'components/hooks/useNotification'
import { useParams } from 'react-router'

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

  useEffect(() => {
    Promise.all([
      getEducationalDomainsAdapter(),
      getVenueEducationalStatusesAdapter(),
      getCulturalPartnersAdapter(),
    ]).then(([domainsResponse, statusesResponse, culturalPartnersResponse]) => {
      if (
        [domainsResponse, statusesResponse, culturalPartnersResponse].some(
          response => !response.isOk
        )
      ) {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      setDomains(domainsResponse.payload)
      setStatuses(statusesResponse.payload)
      setCulturalPartners(culturalPartnersResponse.payload)

      setIsLoading(false)
    })
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
        />
      )}
    </>
  )
}

export default CollectiveDataEdition

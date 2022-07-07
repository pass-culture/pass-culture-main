import React, { useEffect, useState } from 'react'
import {
  getCulturalPartnersAdapter,
  getVenueEducationalStatusesAdapter,
} from './adapters'

import CollectiveDataForm from './CollectiveDataForm'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import { Title } from 'ui-kit'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import styles from './CollectiveDataEdition.module.scss'
import useNotification from 'components/hooks/useNotification'

const CollectiveDataEdition = (): JSX.Element => {
  const notify = useNotification()

  const [domains, setDomains] = useState<SelectOption[]>([])
  const [statuses, setStatuses] = useState<SelectOption[]>([])
  const [culturalPartners, setCulturalPartners] = useState<SelectOption[]>([])

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
    })
  }, [])

  return (
    <>
      <Title level={1}>Mes informations EAC</Title>
      <p className={styles.description}>
        Il s'agit d'un formulaire vous permettant de renseigner vos
        informattions EAC. Les informations renseignées seront visibles par les
        enseignants et chefs d'établissement sur Adage (Application Dédiée A la
        Généralisation de l'Education artistique et culturelle).
      </p>
      <CollectiveDataForm
        statuses={statuses}
        domains={domains}
        culturalPartners={culturalPartners}
      />
    </>
  )
}

export default CollectiveDataEdition

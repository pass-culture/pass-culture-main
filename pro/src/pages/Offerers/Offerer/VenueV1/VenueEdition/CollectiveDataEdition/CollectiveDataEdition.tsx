import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { GetCollectiveVenueResponseModel } from 'apiClient/v1'
import MandatoryInfo from 'components/FormLayout/FormLayoutMandatoryInfo'
import {
  EducationalCategories,
  getEducationalCategoriesAdapter,
  getEducationalDomainsAdapter,
} from 'core/OfferEducational'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { ReactComponent as CircleArrowIcon } from 'icons/full-circle-arrow-left.svg'
import { Banner, Title, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getCulturalPartnersAdapter } from '../adapters'
import { venueHasCollectiveInformation } from '../EACInformation/utils/venueHasCollectiveInformation'

import { getVenueEducationalStatusesAdapter } from './adapters'
import getCulturalPartnerAdapter from './adapters/getCulturalPartnerAdapter'
import getVenueCollectiveDataAdapter from './adapters/getVenueCollectiveDataAdapter'
import styles from './CollectiveDataEdition.module.scss'
import CollectiveDataForm from './CollectiveDataForm'

const fetchCulturalPartnerIfVenueHasNoCollectiveData = async (
  venueResponse: GetCollectiveVenueResponseModel
): Promise<GetCollectiveVenueResponseModel | null> => {
  if (!venueResponse.siret) {
    return null
  }

  const culturalPartnerResponse = await getCulturalPartnerAdapter(
    venueResponse.siret
  )

  if (!culturalPartnerResponse.isOk) {
    return null
  }

  return {
    ...venueResponse,
    collectiveLegalStatus: culturalPartnerResponse.payload.statutId
      ? {
          id: culturalPartnerResponse.payload.statutId,
          name: '',
        }
      : null,
    collectiveWebsite: culturalPartnerResponse.payload.siteWeb,
    collectiveDomains: culturalPartnerResponse.payload.domaineIds.map(id => ({
      id,
      name: '',
    })),
  }
}

const CollectiveDataEdition = (): JSX.Element | null => {
  const notify = useNotification()
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()

  const [domains, setDomains] = useState<SelectOption[]>([])
  const [statuses, setStatuses] = useState<SelectOption[]>([])
  const [culturalPartners, setCulturalPartners] = useState<SelectOption[]>([])
  const [categories, setCategories] = useState<EducationalCategories>({
    educationalCategories: [],
    educationalSubCategories: [],
  })
  const [isLoading, setIsLoading] = useState(true)
  const [venueCollectiveData, setVenueCollectiveData] =
    useState<GetCollectiveVenueResponseModel | null>(null)
  const [adageVenueCollectiveData, setAdageVenueCollectiveData] =
    useState<GetCollectiveVenueResponseModel | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      const allResponses = await Promise.all([
        getEducationalDomainsAdapter(),
        getVenueEducationalStatusesAdapter(),
        getCulturalPartnersAdapter(),
        getVenueCollectiveDataAdapter(Number(venueId) ?? ''),
        getEducationalCategoriesAdapter(),
      ])

      if (allResponses.some(response => !response.isOk)) {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      const [
        domainsResponse,
        statusesResponse,
        culturalPartnersResponse,
        venueResponse,
        categoriesResponse,
      ] = allResponses

      setDomains(domainsResponse.payload)
      setStatuses(statusesResponse.payload)
      setCulturalPartners(culturalPartnersResponse.payload)
      setCategories(categoriesResponse.payload)
      if (venueResponse.isOk) {
        if (venueHasCollectiveInformation(venueResponse.payload)) {
          setVenueCollectiveData(venueResponse.payload)
        } else {
          const collectiveData =
            await fetchCulturalPartnerIfVenueHasNoCollectiveData(
              venueResponse.payload
            )
          setAdageVenueCollectiveData(collectiveData)
        }
      }

      setIsLoading(false)
    }
    if (venueId && offererId) {
      fetchData()
    }
  }, [])
  if (!venueId || !offererId) {
    return null
  }
  return (
    <div>
      <ButtonLink
        link={{
          to: `/structures/${offererId}/lieux/${venueId}#venue-collective-data`,
          isExternal: false,
        }}
        variant={ButtonVariant.TERNARY}
        Icon={CircleArrowIcon}
        className={styles['go-back-link']}
      >
        Retour page lieu
      </ButtonLink>
      <Title level={1} className={styles['title']}>
        Mes informations pour les enseignants
      </Title>
      <Banner type="notification-info">
        Ce formulaire vous permet de renseigner des informations complémentaires
        concernant votre établissement et les actions menées auprès du public
        scolaire. Ces informations seront visibles par les enseignants et chefs
        d'établissement sur ADAGE. Cela leur permettra de mieux comprendre votre
        démarche d'éducation artistique et culturelle.
      </Banner>
      <MandatoryInfo className={styles.mandatory} />
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
          adageVenueCollectiveData={adageVenueCollectiveData}
          categories={categories}
        />
      )}
    </div>
  )
}

export default CollectiveDataEdition

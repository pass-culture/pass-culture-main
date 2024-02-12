import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
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
import Spinner from 'ui-kit/Spinner/Spinner'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

import { getCulturalPartnersAdapter } from '../adapters'
import { venueHasCollectiveInformation } from '../EACInformation/utils/venueHasCollectiveInformation'

import { getVenueEducationalStatusesAdapter } from './adapters'
import getVenueCollectiveDataAdapter from './adapters/getVenueCollectiveDataAdapter'
import styles from './CollectiveDataEdition.module.scss'
import CollectiveDataForm from './CollectiveDataForm'

const fetchCulturalPartnerIfVenueHasNoCollectiveData = async (
  venueResponse: GetCollectiveVenueResponseModel
): Promise<GetCollectiveVenueResponseModel | null> => {
  if (!venueResponse.siret) {
    return null
  }

  try {
    const culturalPartnerResponse = await api.getEducationalPartner(
      venueResponse.siret
    )

    return {
      ...venueResponse,
      collectiveLegalStatus: culturalPartnerResponse.statutId
        ? {
            id: culturalPartnerResponse.statutId,
            name: '',
          }
        : null,
      collectiveWebsite: culturalPartnerResponse.siteWeb,
      collectiveDomains: culturalPartnerResponse.domaineIds.map((id) => ({
        id,
        name: '',
      })),
    }
  } catch (e) {
    sendSentryCustomError(
      `error when fetching cultural educational partner ${e}`
    )

    return null
  }
}

export const CollectiveDataEdition = (): JSX.Element | null => {
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

      if (allResponses.some((response) => !response.isOk)) {
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
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      fetchData()
    }
  }, [])

  if (!venueId || !offererId) {
    return null
  }

  return (
    <>
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
    </>
  )
}

import { addDays, isBefore } from 'date-fns'
import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetCollectiveVenueResponseModel,
  GetVenueResponseModel,
} from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import MandatoryInfo from 'components/FormLayout/FormLayoutMandatoryInfo'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { PartnerPageCollectiveSection } from 'pages/Home/Offerers/PartnerPageCollectiveSection'
import { CollectiveDmsTimeline } from 'pages/VenueCreation/CollectiveDmsTimeline/CollectiveDmsTimeline'
import Spinner from 'ui-kit/Spinner/Spinner'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'
import { venueHasCollectiveInformation } from 'utils/venueHasCollectiveInformation'

import { getCulturalPartnersAdapter } from '../adapters'

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
    sendSentryCustomError(e)

    return null
  }
}

export interface CollectiveDataEditionProps {
  venue?: GetVenueResponseModel
}

export const CollectiveDataEdition = ({
  venue,
}: CollectiveDataEditionProps): JSX.Element | null => {
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
  const [adageVenueCollectiveData, setAdageVenueCollectiveData] =
    useState<GetCollectiveVenueResponseModel | null>(null)
  const [canCreateCollectiveOffer, setCanCreateCollectiveOffer] = useState<
    boolean | null
  >(null)

  useEffect(() => {
    const fetchData = async () => {
      const allResponses = await Promise.all([
        getEducationalDomainsAdapter(),
        getVenueEducationalStatusesAdapter(),
        getCulturalPartnersAdapter(),
        getVenueCollectiveDataAdapter(Number(venueId) ?? ''),
      ])

      try {
        const { canCreate: canOffererCreateCollectiveOffer } =
          await api.canOffererCreateEducationalOffer(Number(offererId))
        setCanCreateCollectiveOffer(canOffererCreateCollectiveOffer)
      } catch {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      if (allResponses.some((response) => !response.isOk)) {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      const [
        domainsResponse,
        statusesResponse,
        culturalPartnersResponse,
        venueResponse,
      ] = allResponses

      setDomains(domainsResponse.payload)
      setStatuses(statusesResponse.payload)
      setCulturalPartners(culturalPartnersResponse.payload)
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

  if (!venueId || !offererId || !venue || isLoading) {
    return <Spinner className={styles.spinner} />
  }

  const hasAdageIdForMoreThan30Days = Boolean(
    venue?.hasAdageId &&
      venue?.adageInscriptionDate &&
      isBefore(new Date(venue?.adageInscriptionDate), addDays(new Date(), -30))
  )

  const showCollectiveDataForm = Boolean(
    venue?.hasAdageId && canCreateCollectiveOffer
  )
  const collectiveDmsApplication = getLastCollectiveDmsApplication(
    venue.collectiveDmsApplications
  )

  return (
    <>
      {showCollectiveDataForm && (
        <Callout title="Les informations suivantes sont visibles par les enseignants et établissements sur ADAGE">
          Cela leur permet de mieux comprendre votre démarche d’éducation
          artistique et culturelle.
        </Callout>
      )}

      <PartnerPageCollectiveSection
        venueId={venue.id}
        hasAdageId={venue.hasAdageId}
        collectiveDmsApplications={venue.collectiveDmsApplications}
      />

      {collectiveDmsApplication && (
        <div className={styles['timeline']}>
          <CollectiveDmsTimeline
            collectiveDmsApplication={collectiveDmsApplication}
            hasAdageId={venue.hasAdageId}
            hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
            adageInscriptionDate={venue.adageInscriptionDate}
          />
        </div>
      )}

      {showCollectiveDataForm && (
        <>
          <MandatoryInfo className={styles.mandatory} />

          <CollectiveDataForm
            statuses={statuses}
            domains={domains}
            culturalPartners={culturalPartners}
            venue={venue}
            venueCollectiveData={venueCollectiveData}
            adageVenueCollectiveData={adageVenueCollectiveData}
          />
        </>
      )}
    </>
  )
}

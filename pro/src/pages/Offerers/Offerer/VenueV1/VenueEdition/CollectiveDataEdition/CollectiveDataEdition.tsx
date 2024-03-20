import { addDays, isBefore } from 'date-fns'
import React, { useEffect, useState } from 'react'
import { Route, Routes, useParams } from 'react-router-dom'

import { GetVenueResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { PartnerPageCollectiveSection } from 'pages/Home/Offerers/PartnerPageCollectiveSection'
import { CollectiveDmsTimeline } from 'pages/VenueCreation/CollectiveDmsTimeline/CollectiveDmsTimeline'
import Spinner from 'ui-kit/Spinner/Spinner'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import { getCulturalPartnersAdapter } from '../adapters'

import { getVenueEducationalStatusesAdapter } from './adapters'
import styles from './CollectiveDataEdition.module.scss'
import { CollectiveDataEditionReadOnly } from './CollectiveDataEditionReadOnly'
import { CollectiveDataForm } from './CollectiveDataForm/CollectiveDataForm'

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
  const canCreateCollectiveOffer = venue?.managingOfferer.allowedOnAdage

  useEffect(() => {
    const fetchData = async () => {
      const allResponses = await Promise.all([
        getEducationalDomainsAdapter(),
        getVenueEducationalStatusesAdapter(),
        getCulturalPartnersAdapter(),
      ])

      if (allResponses.some((response) => !response.isOk)) {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      const [domainsResponse, statusesResponse, culturalPartnersResponse] =
        allResponses

      setDomains(domainsResponse.payload)
      setStatuses(statusesResponse.payload)
      setCulturalPartners(culturalPartnersResponse.payload)

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
        collectiveDmsApplications={venue.collectiveDmsApplications}
        allowedOnAdage={venue.managingOfferer.allowedOnAdage}
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
          <hr className={styles['separator']} />

          <Routes>
            <Route
              path=""
              element={
                <CollectiveDataEditionReadOnly
                  venue={venue}
                  culturalPartners={culturalPartners}
                />
              }
            />
            <Route
              path="/edition"
              element={
                <CollectiveDataForm
                  statuses={statuses}
                  domains={domains}
                  culturalPartners={culturalPartners}
                  venue={venue}
                />
              }
            />
          </Routes>
        </>
      )}
    </>
  )
}

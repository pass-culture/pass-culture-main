import { addDays, isBefore } from 'date-fns'
import { Route, Routes, useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import {
  GET_CULTURAL_PARTNERS_QUERY_KEY,
  GET_EDUCATIONAL_DOMAINS_QUERY_KEY,
  GET_EDUCATIONAL_STATUSES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { SelectOption } from 'custom_types/form'
import { PartnerPageCollectiveSection } from 'pages/Home/Offerers/PartnerPageCollectiveSection'
import { CollectiveDmsTimeline } from 'pages/VenueCreation/CollectiveDmsTimeline/CollectiveDmsTimeline'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import styles from './CollectiveDataEdition.module.scss'
import { CollectiveDataEditionReadOnly } from './CollectiveDataEditionReadOnly'
import { CollectiveDataForm } from './CollectiveDataForm/CollectiveDataForm'

export interface CollectiveDataEditionProps {
  venue?: GetVenueResponseModel
}

export const CollectiveDataEdition = ({
  venue,
}: CollectiveDataEditionProps): JSX.Element | null => {
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()

  const domainsQuery = useSWR([GET_EDUCATIONAL_DOMAINS_QUERY_KEY], () =>
    api.listEducationalDomains()
  )
  const educationalStatusesQuery = useSWR(
    [GET_EDUCATIONAL_STATUSES_QUERY_KEY],
    () => api.getVenuesEducationalStatuses()
  )
  const culturalPartnersQuery = useSWR([GET_CULTURAL_PARTNERS_QUERY_KEY], () =>
    api.getEducationalPartners()
  )
  const domains: SelectOption[] =
    domainsQuery.data?.map((domain) => ({
      value: domain.id.toString(),
      label: domain.name,
    })) ?? []
  const statuses: SelectOption[] =
    educationalStatusesQuery.data?.statuses.map((status) => ({
      value: status.id,
      label: status.name,
    })) ?? []
  const culturalPartners: SelectOption[] =
    culturalPartnersQuery.data?.partners.map((culturalPartner) => ({
      value: culturalPartner.id.toString(),
      label: culturalPartner.libelle,
    })) ?? []

  const canCreateCollectiveOffer = venue?.managingOfferer.allowedOnAdage

  if (
    !venueId ||
    !offererId ||
    !venue ||
    domainsQuery.isLoading ||
    educationalStatusesQuery.isLoading ||
    culturalPartnersQuery.isLoading
  ) {
    return <Spinner className={styles.spinner} />
  }

  const hasAdageIdForMoreThan30Days = Boolean(
    venue.hasAdageId &&
      venue.adageInscriptionDate &&
      isBefore(new Date(venue.adageInscriptionDate), addDays(new Date(), -30))
  )

  const showCollectiveDataForm = Boolean(
    venue.hasAdageId && canCreateCollectiveOffer
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
        venueName={venue.name}
        offererId={venue.managingOfferer.id}
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

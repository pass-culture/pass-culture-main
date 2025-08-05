import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { GET_EDUCATIONAL_STATUSES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { SelectOption } from 'commons/custom_types/form'
import { useEducationalDomains } from 'commons/hooks/swr/useEducationalDomains'
import { getLastCollectiveDmsApplication } from 'commons/utils/getLastCollectiveDmsApplication'
import { addDays, isBefore } from 'date-fns'
import { PartnerPageCollectiveSection } from 'pages/Homepage/components/Offerers/components/PartnerPages/components/PartnerPageCollectiveSection'
import { useLocation, useParams } from 'react-router'
import useSWR from 'swr'
import { Callout } from 'ui-kit/Callout/Callout'
import { Option } from 'ui-kit/MultiSelect/MultiSelect'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { CollectiveDmsTimeline } from '../CollectiveDmsTimeline/CollectiveDmsTimeline'

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

  const { data: educationalDomains, isLoading: areEducationalDomainsLoading } =
    useEducationalDomains()

  const educationalStatusesQuery = useSWR(
    [GET_EDUCATIONAL_STATUSES_QUERY_KEY],
    () => api.getVenuesEducationalStatuses()
  )

  const domains: Option[] = educationalDomains.map((domain) => ({
    id: domain.id.toString(),
    label: domain.name,
  }))

  const statuses: SelectOption[] =
    educationalStatusesQuery.data?.statuses.map((status) => ({
      value: status.id.toString(),
      label: status.name,
    })) ?? []

  const canCreateCollectiveOffer = venue?.managingOfferer.allowedOnAdage

  const location = useLocation()

  if (
    !venueId ||
    !offererId ||
    !venue ||
    areEducationalDomainsLoading ||
    educationalStatusesQuery.isLoading
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

          {location.pathname.includes('/edition') ? (
            <CollectiveDataForm
              statuses={statuses}
              domains={domains}
              venue={venue}
            />
          ) : (
            <CollectiveDataEditionReadOnly venue={venue} />
          )}
        </>
      )}
    </>
  )
}

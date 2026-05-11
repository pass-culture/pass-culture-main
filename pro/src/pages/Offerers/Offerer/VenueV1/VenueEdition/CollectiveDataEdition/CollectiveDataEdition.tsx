import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_EDUCATIONAL_STATUSES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import type { SelectOption } from '@/commons/custom_types/form'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { CollectiveDmsTimeline } from '@/components/CollectiveDmsTimeline/CollectiveDmsTimeline'
import { Banner } from '@/design-system/Banner/Banner'
import { PartnerPageCollectiveSection } from '@/pages/Homepage/components/Offerers/components/PartnerPages/components/PartnerPageCollectiveSection'
import type { Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './CollectiveDataEdition.module.scss'
import { CollectiveDataEditionReadOnly } from './CollectiveDataEditionReadOnly'
import { CollectiveDataForm } from './CollectiveDataForm/CollectiveDataForm'

export const CollectiveDataEdition = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
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

  const location = useLocation()

  if (areEducationalDomainsLoading || educationalStatusesQuery.isLoading) {
    return <Spinner className={styles.spinner} />
  }

  const showCollectiveDataForm = Boolean(
    selectedPartnerVenue.hasAdageId && selectedPartnerVenue.allowedOnAdage
  )

  return (
    <>
      {showCollectiveDataForm && (
        <Banner
          title="Les informations suivantes sont visibles par les enseignants et établissements sur ADAGE"
          description="Cela leur permet de mieux comprendre votre démarche d’éducation artistique et culturelle."
        />
      )}

      <PartnerPageCollectiveSection />

      {selectedPartnerVenue.lastCollectiveDmsApplication && (
        <div className={styles['timeline']}>
          <CollectiveDmsTimeline
            collectiveDmsApplication={
              selectedPartnerVenue.lastCollectiveDmsApplication
            }
            hasAdageId={selectedPartnerVenue.hasAdageId}
            adageInscriptionDate={selectedPartnerVenue.adageInscriptionDate}
          />
        </div>
      )}

      {showCollectiveDataForm && (
        <>
          <hr className={styles['separator']} />

          {location.pathname.includes('/edition') ? (
            <CollectiveDataForm statuses={statuses} domains={domains} />
          ) : (
            <CollectiveDataEditionReadOnly />
          )}
        </>
      )}
    </>
  )
}

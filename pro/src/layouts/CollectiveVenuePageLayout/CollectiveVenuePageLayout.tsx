import { Outlet } from 'react-router'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { CollectiveDmsTimeline } from '@/components/CollectiveDmsTimeline/CollectiveDmsTimeline'
import { Banner } from '@/design-system/Banner/Banner'

import styles from './CollectiveVenuePageLayout.module.scss'
import { PartnerPageCollectiveSection } from './components/PartnerPageCollectiveSection'

export const CollectiveVenuePageLayout = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isActiveOnAdage = Boolean(
    selectedPartnerVenue.hasAdageId && selectedPartnerVenue.allowedOnAdage
  )

  return (
    <>
      {isActiveOnAdage && (
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

      {isActiveOnAdage && (
        <>
          <hr className={styles['separator']} />

          <Outlet />
        </>
      )}
    </>
  )
}

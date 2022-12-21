import React, { useRef } from 'react'

import { useAppContext } from 'app/AppContext'
import JobHighlightsBanner from 'components/JobHighlightsBanner'
import PageTitle from 'components/PageTitle/PageTitle'
import useActiveFeature from 'hooks/useActiveFeature'
import { Title } from 'ui-kit'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './CompanyHome.module.scss'
import { OffererStats } from './OffererStats'
import { Venue } from './Venues'

const CompanyHome = (): JSX.Element => {
  const profileRef = useRef(null)
  const statsRef = useRef(null)
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const isJobHighlightBannerEnabled = useActiveFeature(
    'TEMP_ENABLE_JOB_HIGHLIGHTS_BANNER'
  )
  const { selectedVenue, selectedOffererId } = useAppContext()

  if (selectedVenue === null || selectedOffererId === null) {
    return <Spinner />
  }

  return (
    <div className="homepage">
      <PageTitle title="Mon entreprise" />
      <Title className={styles['page-title']} level={1}>
        Bienvenue dans l’espace acteurs culturels
      </Title>
      {isJobHighlightBannerEnabled && <JobHighlightsBanner />}
      {selectedVenue?.isVirtual ? (
        <Venue
          hasBusinessUnit={!!selectedVenue.businessUnitId}
          id={selectedVenue.id}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={!selectedVenue.businessUnitId}
          hasOnlyOneVenue={true}
        />
      ) : (
        <Venue
          hasBusinessUnit={!!selectedVenue.businessUnitId}
          id={selectedVenue.id}
          key={selectedVenue.id}
          name={selectedVenue.name}
          offererId={selectedOffererId}
          publicName={selectedVenue.publicName || undefined}
          hasMissingReimbursementPoint={!selectedVenue.businessUnitId}
          hasOnlyOneVenue={true}
        />
      )}

      {isOffererStatsActive && (
        <section className="h-section" ref={statsRef}>
          <OffererStats />
        </section>
      )}
    </div>
  )
}

export default CompanyHome

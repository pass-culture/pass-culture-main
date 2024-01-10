import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { Card } from '../Card'
import {
  getVirtualVenueFromOfferer,
  getPhysicalVenuesFromOfferer,
} from '../venueUtils'

import styles from './VenueCreationLinks.module.scss'

interface VenueCreationLinksProps {
  offerer?: GetOffererResponseModel | null
}

export const VenueCreationLinks = ({ offerer }: VenueCreationLinksProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const isStatisticsDashboardEnabled = useActiveFeature('WIP_HOME_STATS')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const virtualVenue = getVirtualVenueFromOfferer(offerer)
  const physicalVenues = getPhysicalVenuesFromOfferer(offerer)
  const hasVirtualOffers = Boolean(virtualVenue)
  const hasPhysicalVenue = physicalVenues?.length > 0

  if (!hasPhysicalVenue) {
    return
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offerer?.id}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const renderLinks = (insideCard: boolean) => {
    return (
      <div className={styles['actions-container']}>
        <ButtonLink
          variant={insideCard ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY}
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent?.(Events.CLICKED_CREATE_VENUE, {
              from: location.pathname,
              is_first_venue: !hasPhysicalVenue && !hasVirtualOffers,
            })
          }}
        >
          {!hasPhysicalVenue ? 'Créer un lieu' : 'Ajouter un lieu'}
        </ButtonLink>

        {!isStatisticsDashboardEnabled && (
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: `/offre/creation?structure=${offerer?.id}`,
              isExternal: false,
            }}
          >
            Créer une offre
          </ButtonLink>
        )}
      </div>
    )
  }

  const renderCard = () => (
    <Card data-testid="offerers-creation-links-card">
      <h3 className={styles['title']}>Lieux</h3>

      <div className={styles['content']}>
        <p>
          Avant de créer votre première offre physique vous devez avoir un lieu
        </p>
        {renderLinks(true)}
      </div>
    </Card>
  )

  return (
    <div className={styles['container']}>
      {!(hasPhysicalVenue || hasVirtualOffers)
        ? renderCard()
        : renderLinks(false)}
    </div>
  )
}

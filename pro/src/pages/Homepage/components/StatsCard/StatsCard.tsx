import { useAnalytics } from 'app/App/analytics/firebase'
import cn from 'classnames'
import { HomepageEvents } from 'commons/core/FirebaseEvents/constants'
import headlineImg from 'components/IndividualOfferLayout/components/OfferHeadlineCard/assets/headline-img.svg'
import { Button } from 'design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from 'design-system/Button/types'
import useSWR from 'swr'
import { Select } from 'ui-kit/form/Select/Select'
import { Skeleton } from 'ui-kit/Skeleton/Skeleton'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import {
  GET_VENUES_OFFERS_STATS_V2,
  GET_VENUES_STATS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import strokeShowIcon from '@/icons/stroke-show.svg'
import { Card } from '@/ui-kit/Card/Card'

import { CumulatedViews } from './components/CumulatedViews'
import { MostViewedOffers } from './components/MostViewedOffers'
import styles from './StatsCard.module.scss'

interface StatsCardProps {
  venue: GetVenueResponseModel
}

export const StatsCard = ({ venue }: StatsCardProps) => {
  const isStatsV2 = useActiveFeature('WIP_HOME_STATS_V2')
  const { logEvent } = useAnalytics()

  const { data: oldStats } = useSWR(
    [GET_VENUES_STATS_QUERY_KEY, venue.id],
    ([, venueId]) => api.getVenueOffersStats({ path: { venue_id: venueId } })
  )

  const { data: stats, isLoading } = useSWR(
    [GET_VENUES_OFFERS_STATS_V2, venue.id],
    ([, venueId]) =>
      api.getVenueOffersStatsV2({
        path: { venue_id: venueId },
      })
  )

  const dailyViews = oldStats?.jsonData.dailyViews ?? []

  if (!oldStats || dailyViews.length < 2) {
    return null
  }

  const { topOffers, totalViewsLast30Days } = oldStats.jsonData

  const oldStatsComponent = (
    <Card>
      <Card.Header title="Les statistiques sur l'individuel" />
      <Card.Content>
        <div
          className={cn(styles['data-container'], {
            [styles['has-top-offers']]: topOffers.length > 0,
          })}
        >
          <CumulatedViews
            dailyViews={dailyViews}
            totalViewsLast30Days={totalViewsLast30Days}
            showTitle={false}
          />
          {topOffers.length > 0 && <MostViewedOffers topOffers={topOffers} />}
        </div>
      </Card.Content>
    </Card>
  )

  const newStatsComponent = (
    <Card>
      {isLoading && <Skeleton height="339px" width="100%" />}
      {!isLoading && (
        <>
          <Card.Header title="Statistiques de vos offres individuelles">
            <Select
              className={styles['stats-select']}
              name="stats-period"
              label=""
              options={[
                { value: 'last3Months', label: '3 derniers mois' },
                { value: 'last6Months', label: '6 derniers mois' },
              ]}
              onChange={(event) =>
                logEvent(HomepageEvents.CHANGED_STATS_V2_PERIOD, {
                  period: event.target.value,
                })
              }
            />
          </Card.Header>
          <Card.Content>
            <div
              className={cn(styles['stats-wrapper'], {
                [styles['has-top-offers']]: topOffers.length > 0,
              })}
            >
              <div>
                <div className={styles['stats-chart-title']}>
                  <div className={styles['stats-chart-title-icon']}>
                    <SvgIcon src={strokeShowIcon} width="32" />
                  </div>
                  <div>
                    <p className={styles['stats-chart-title-main']}>
                      {stats?.last3Months.cumulatedViews} consultations
                    </p>
                    <p className={styles['stats-chart-title-sub']}>
                      sur les XXXXX
                    </p>
                  </div>
                </div>
                GRAPHE
              </div>
              {topOffers.length > 0 && (
                <MostViewedOffers topOffers={topOffers} />
              )}
            </div>
            <div>
              <h3 className={styles['stats-headline-offer-head']}>
                Améliorez votre visibilité
              </h3>
              <div className={styles['stats-headline-offer']}>
                <SvgIcon
                  src={headlineImg}
                  alt=""
                  width="68"
                  viewBox="0 0 68 68"
                  aria-hidden={true}
                />
                <p className={styles['stats-headline-offer-title']}>
                  Doublez les consultations d’une offre en la mettant à la une
                </p>
                <div className={styles['stats-headline-offer-button']}>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                    size={ButtonSize.SMALL}
                    label="Choisir une offre"
                  />
                </div>
              </div>
            </div>
          </Card.Content>
        </>
      )}
    </Card>
  )

  return isStatsV2 ? newStatsComponent : oldStatsComponent
}

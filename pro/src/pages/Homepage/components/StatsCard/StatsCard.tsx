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
import { useEffect, useState } from 'react'
import useSWR from 'swr'
import { Select } from 'ui-kit/form/Select/Select'
import { Skeleton } from 'ui-kit/Skeleton/Skeleton'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUES_STATS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
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
  const [isLoading, setIsLoading] = useState(true)
  const isStatsV2 = useActiveFeature('WIP_HOME_STATS_V2')
  const { logEvent } = useAnalytics()

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setIsLoading(false)
    }, 3000)

    return () => {
      clearTimeout(timeoutId)
    }
  }, [])

  const { data: stats } = useSWR(
    [GET_VENUES_STATS_QUERY_KEY, venue.id],
    ([, venueId]) => api.getVenueOffersStats({ path: { venue_id: venueId } })
  )

  const dailyViews = stats?.jsonData.dailyViews ?? []

  if (!stats || dailyViews.length < 2) {
    return null
  }

  const { topOffers, totalViewsLast30Days } = stats.jsonData

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
              <div className={styles['stats-chart']}>
                <div className={styles['stats-chart-title']}>
                  <div className={styles['stats-chart-title-icon']}>
                    <SvgIcon src={strokeShowIcon} width="32" />
                  </div>
                  <div>
                    <h3 className={styles['stats-chart-title-main']}>
                      XXX consultations
                    </h3>
                    <h4 className={styles['stats-chart-title-sub']}>
                      sur les XXXXX
                    </h4>
                  </div>
                </div>
                GRAPHE
              </div>
              {topOffers.length > 0 && (
                <MostViewedOffers topOffers={topOffers} />
              )}
            </div>
            <div>
              <h3>Améliorez votre visibilité</h3>
              <div className={styles['stats-headline-offer']}>
                <SvgIcon
                  src={headlineImg}
                  alt=""
                  width="68"
                  viewBox="0 0 68 68"
                  aria-hidden={true}
                  className={styles['stats-headline-offer-icon']}
                />
                <h4 className={styles['stats-headline-offer-title']}>
                  Doublez les consultations d’une offre en la mettant à la une
                </h4>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  size={ButtonSize.SMALL}
                  label="Choisir une offre à mettre à la une"
                />
              </div>
            </div>
          </Card.Content>
        </>
      )}
    </Card>
  )

  return isStatsV2 ? newStatsComponent : oldStatsComponent
}

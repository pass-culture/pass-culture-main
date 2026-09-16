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
import { CumulatedViews } from 'pages/Homepage/components/StatsCard/components/CumulatedViews'
import { OldMostViewedOffers } from 'pages/Homepage/components/StatsCard/components/OldMostViewedOffers'
import { useEffect, useState } from 'react'
import useSWR from 'swr'
import { Select } from 'ui-kit/form/Select/Select'
import { Skeleton } from 'ui-kit/Skeleton/Skeleton'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { api } from '@/apiClient/api'
import type {
  GetVenueResponseModel,
  VenueOffersPeriodStatsModel,
} from '@/apiClient/v1'
import {
  GET_VENUES_OFFERS_STATS_V2,
  GET_VENUES_STATS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import strokeShowIcon from '@/icons/stroke-show.svg'
import { Card } from '@/ui-kit/Card/Card'

import { MostViewedOffers } from './components/MostViewedOffers'
import { OldCumulatedViews } from './components/OldCumulatedViews'
import styles from './StatsCard.module.scss'

interface StatsCardProps {
  venue: GetVenueResponseModel
}

type StatsPeriods = 'last3Months' | 'last6Months'

export const StatsCard = ({ venue }: StatsCardProps) => {
  const isStatsV2 = useActiveFeature('WIP_HOME_STATS_V2')
  const [selectedPeriod, setSelectedPeriod] = useState<StatsPeriods>()
  const [periodStats, setPeriodStats] = useState<VenueOffersPeriodStatsModel>()
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

  if (isStatsV2 && !selectedPeriod && !isLoading) {
    if (
      (stats?.last3Months.cumulatedViews ?? 0) <= 0 &&
      (stats?.last6Months.cumulatedViews ?? 0) > 0
    ) {
      setSelectedPeriod('last6Months')
    } else {
      setSelectedPeriod('last3Months')
    }
  }

  useEffect(() => {
    if (selectedPeriod === 'last6Months') {
      setPeriodStats(stats?.last6Months)
    } else if (selectedPeriod === 'last3Months') {
      setPeriodStats(stats?.last3Months)
    }
  }, [selectedPeriod, periodStats, stats])

  const dailyViews = oldStats?.jsonData.dailyViews ?? []

  if (!isStatsV2 && (!oldStats || dailyViews.length < 2)) {
    return null
  }

  const oldStatsComponent = (
    <Card>
      <Card.Header title="Les statistiques sur l'individuel" />
      <Card.Content>
        <div
          className={cn(styles['data-container'], {
            [styles['has-top-offers']]:
              (oldStats?.jsonData?.topOffers?.length ?? 0) > 0,
          })}
        >
          <OldCumulatedViews
            dailyViews={dailyViews}
            totalViewsLast30Days={oldStats?.jsonData?.totalViewsLast30Days ?? 0}
            showTitle={false}
          />
          {(oldStats?.jsonData?.topOffers?.length ?? 0) > 0 && (
            <OldMostViewedOffers
              topOffers={oldStats?.jsonData?.topOffers ?? []}
            />
          )}
        </div>
      </Card.Content>
    </Card>
  )

  const newStatsComponent = (
    <Card>
      {isLoading && <Skeleton height="339px" width="100%" />}
      {isStatsV2 && !isLoading && (
        <>
          <Card.Header title="Statistiques de vos offres individuelles">
            <Select
              className={styles['stats-select']}
              name="stats-period"
              ariaLabel="Période de statistiques"
              label=""
              value={selectedPeriod}
              options={[
                { value: 'last3Months', label: '3 derniers mois' },
                { value: 'last6Months', label: '6 derniers mois' },
              ]}
              onChange={(event) => {
                setSelectedPeriod(event.target.value as StatsPeriods)
                logEvent(HomepageEvents.CHANGED_STATS_V2_PERIOD, {
                  period: event.target.value,
                })
              }}
            />
          </Card.Header>
          <Card.Content>
            <div
              className={cn(styles['stats-wrapper'], {
                [styles['has-top-offers']]:
                  (oldStats?.jsonData?.topOffers?.length ?? 0) > 0,
              })}
            >
              <div>
                <div className={styles['stats-chart-title']}>
                  <div
                    className={cn(styles['stats-chart-title-icon'], {
                      [styles['stats-chart-title-icon-no-data']]:
                        (periodStats?.cumulatedViews ?? 0) <= 0,
                    })}
                  >
                    <SvgIcon src={strokeShowIcon} width="32" />
                  </div>
                  <div>
                    <p className={styles['stats-chart-title-main']}>
                      {periodStats?.cumulatedViews} consultations
                    </p>
                    <p className={styles['stats-chart-title-sub']}>
                      sur les{' '}
                      {selectedPeriod === 'last3Months'
                        ? '3 derniers mois'
                        : '6 derniers mois'}
                    </p>
                  </div>
                </div>
                <CumulatedViews periodStats={periodStats} />
              </div>
              <MostViewedOffers
                topOffers={periodStats?.topOffers ?? []}
                hasActiveIndividualOffer={venue.hasActiveIndividualOffer}
              />
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

import { useAnalytics } from 'app/App/analytics/firebase'
import cn from 'classnames'
import {
  EngagementEvents,
  HomepageEvents,
} from 'commons/core/FirebaseEvents/constants'
import { Button } from 'design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from 'design-system/Button/types'
import { ModalHighlight } from 'pages/Homepage/components/HighlightHome/ModalHighlight/ModalHighlight'
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
  GET_OFFERS_HOME_QUERY_KEY,
  GET_VENUE_HEADLINE_OFFER_QUERY_KEY,
  GET_VENUES_OFFERS_STATS_V2,
  GET_VENUES_STATS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import strokeShowIcon from '@/icons/stroke-show.svg'
import { Card } from '@/ui-kit/Card/Card'

import headlineImg from './assets/headlineImg.svg'
import highlightImg from './assets/highlightImg.svg'
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
  const [isHighlightModalOpen, setIsHighlightModalOpen] = useState(false)
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

  const { data: individualOffers = [], isLoading: areOffersLoading } = useSWR(
    isStatsV2 ? [GET_OFFERS_HOME_QUERY_KEY, venue.id] : null,
    () => api.listOffersHome({ query: { venueId: venue.id } }),
    { fallbackData: [] }
  )

  const { data: rawHeadlineOffer } = useSWR(
    [GET_VENUE_HEADLINE_OFFER_QUERY_KEY],
    () => api.getVenueHeadlineOffer({ path: { venue_id: venue.id } }),
    {
      onError: (error) => {
        // 404 is expected when there is no headline offer.
        if (error.status !== 404) {
          throw error
        }
      },
      onErrorRetry: (error) => {
        // By default, SWR retries on error. We don't want to retry on 404,
        // since it's expected when there is no headline offer.
        if (error.status === 404) {
          return
        }
      },
    }
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
  const hasThingOffers = individualOffers.some((offer) => !offer.isEvent)
  const hasEventOffers = individualOffers.some((offer) => offer.isEvent)
  const hasBothOfferTypes = hasThingOffers && hasEventOffers

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
            {!areOffersLoading &&
              ((hasThingOffers && !rawHeadlineOffer) || hasEventOffers) && (
                <div>
                  <h3 className={styles['stats-headline-offer-head']}>
                    Améliorez votre visibilité
                  </h3>
                  <div
                    data-testid="visibility-actions"
                    className={cn(styles['visibility-actions'], {
                      [styles['has-both-actions']]: hasBothOfferTypes,
                    })}
                  >
                    {hasThingOffers && !rawHeadlineOffer && (
                      <div
                        className={cn(
                          styles['visibility-action'],
                          styles['headline-action']
                        )}
                      >
                        <SvgIcon
                          src={headlineImg}
                          alt=""
                          width="68"
                          viewBox="0 0 68 68"
                          aria-hidden={true}
                        />
                        <p className={styles['visibility-action-title']}>
                          Doublez les consultations d’une offre en la mettant à
                          la une
                        </p>
                        <div className={styles['visibility-action-button']}>
                          <Button
                            as="router-link"
                            to="/offres"
                            variant={ButtonVariant.SECONDARY}
                            color={ButtonColor.NEUTRAL}
                            size={ButtonSize.SMALL}
                            fullWidth
                            onClick={() =>
                              logEvent(HomepageEvents.CLICKED_HEADLINE_OFFER)
                            }
                            label="Choisir une offre"
                          />
                        </div>
                      </div>
                    )}
                    {hasEventOffers && !rawHeadlineOffer && (
                      <div
                        className={cn(
                          styles['visibility-action'],
                          styles['highlight-action']
                        )}
                      >
                        <SvgIcon
                          src={highlightImg}
                          alt=""
                          width="68"
                          viewBox="0 0 68 68"
                          aria-hidden={true}
                        />
                        <p className={styles['visibility-action-title']}>
                          Participez à un des temps forts valorisés sur
                          l’application
                        </p>
                        <div className={styles['visibility-action-button']}>
                          <Button
                            variant={ButtonVariant.SECONDARY}
                            color={ButtonColor.NEUTRAL}
                            size={ButtonSize.SMALL}
                            fullWidth
                            onClick={() => {
                              logEvent(
                                EngagementEvents.HAS_REQUESTED_HIGHLIGHTS,
                                {
                                  action: 'discover',
                                }
                              )
                              setIsHighlightModalOpen(true)
                            }}
                            label="Voir les prochains temps forts"
                          />
                        </div>
                      </div>
                    )}
                    {hasEventOffers && rawHeadlineOffer && (
                      <>
                        <p>
                          Si les consultations tardent à venir, pensez à ajuster
                          vos visuels ou le descriptif de vos offres pour
                          captiver encore plus les jeunes.
                        </p>
                        <Button
                          variant={ButtonVariant.TERTIARY}
                          as="a"
                          to="https://aide.passculture.app/hc/fr/sections/4412332363793-Gestion-et-valorisation-des-offres"
                          opensInNewTab
                          label="Voir nos conseils des gestion et valorisation d’offres"
                        />
                      </>
                    )}
                  </div>
                  {hasEventOffers && (
                    <ModalHighlight
                      isOpen={isHighlightModalOpen}
                      onClose={() => setIsHighlightModalOpen(false)}
                    />
                  )}
                </div>
              )}
          </Card.Content>
        </>
      )}
    </Card>
  )

  return isStatsV2 ? newStatsComponent : oldStatsComponent
}

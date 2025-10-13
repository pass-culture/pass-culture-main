import cn from 'classnames'
import { format } from 'date-fns'
import { useEffect, useState } from 'react'

import { api } from '@/apiClient/api'
import type {
  GetOffererResponseModel,
  GetOffererStatsResponseModel,
} from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { Card as HomeCard } from '@/components/Card/Card'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CumulatedViews } from './components/CumulatedViews'
import { HighlightHome } from './components/HighlightHome/HighlightHome'
import { MostViewedOffers } from './components/MostViewedOffers'
import { OfferStats } from './components/OfferStats'
import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  offerer: GetOffererResponseModel
}

export const StatisticsDashboard = ({ offerer }: StatisticsDashboardProps) => {
  const [stats, setStats] = useState<GetOffererStatsResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const areHighlightsEnable = useActiveFeature('WIP_HIGHLIGHT')

  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true)
      const response = await api.getOffererStats(offerer.id)
      setStats(response)
      setIsLoading(false)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStats()
  }, [offerer.id])

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['title']}>
          Présence sur l’application pass Culture
        </h2>
      </div>

      <div className={styles['container-stats-highlight']}>
        {!isLoading && (
          <>
            <HomeCard className={styles['card-data']}>
              {stats?.jsonData.topOffers.length ||
              stats?.jsonData.dailyViews.length ? (
                <div
                  className={cn(styles['data-container'], {
                    [styles['has-top-offers']]:
                      stats.jsonData.topOffers.length > 0,
                  })}
                >
                  <CumulatedViews dailyViews={stats.jsonData.dailyViews} />

                  {stats.jsonData.topOffers.length > 0 && (
                    <MostViewedOffers
                      last30daysViews={stats.jsonData.totalViewsLast30Days}
                      topOffers={stats.jsonData.topOffers}
                    />
                  )}
                  {stats?.syncDate ? (
                    <div className={styles['sync-date']}>
                      Dernière mise à jour :{' '}
                      {format(
                        new Date(stats.syncDate),
                        FORMAT_DD_MM_YYYY_HH_mm
                      )}
                    </div>
                  ) : null}
                </div>
              ) : (
                <div className={styles['no-data']}>
                  <SvgIcon
                    src={strokeNoBookingIcon}
                    alt=""
                    className={styles['no-data-icon']}
                    width="42"
                  />

                  {offerer.hasActiveOffer
                    ? 'Les statistiques de consultation de vos offres seront bientôt disponibles.'
                    : 'Créez vos premières offres grand public pour être visible par les bénéficiaires'}
                </div>
              )}
            </HomeCard>
            {areHighlightsEnable && <HighlightHome />}
          </>
        )}
      </div>

      <OfferStats offerer={offerer} className={styles['offer-stats']} />
    </>
  )
}

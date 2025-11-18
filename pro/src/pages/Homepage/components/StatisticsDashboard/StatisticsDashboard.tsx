import cn from 'classnames'
import { useEffect, useState } from 'react'

import { api } from '@/apiClient/api'
import type {
  GetOffererStatsResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY_HH_mm, formatDate } from '@/commons/utils/date'
import { Card as HomeCard } from '@/components/Card/Card'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CumulatedViews } from './components/CumulatedViews'
import { MostViewedOffers } from './components/MostViewedOffers'
import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  venue: GetVenueResponseModel
}

export const StatisticsDashboard = ({ venue }: StatisticsDashboardProps) => {
  const [stats, setStats] = useState<GetOffererStatsResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true)
      const response = await api.getOffererStats(venue.managingOfferer.id)
      setStats(response)
      setIsLoading(false)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStats()
  }, [venue.managingOfferer.id])

  return (
    <>
      {!isLoading && (
        <HomeCard className={styles['card-data']}>
          {stats?.jsonData.topOffers.length ||
          stats?.jsonData.dailyViews.length ? (
            <div
              className={cn(styles['data-container'], {
                [styles['has-top-offers']]: stats.jsonData.topOffers.length > 0,
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
                  {formatDate(stats.syncDate, FORMAT_DD_MM_YYYY_HH_mm)}
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

              {venue.hasActiveOffer
                ? 'Les statistiques de consultation de vos offres seront bientôt disponibles.'
                : 'Créez vos premières offres grand public pour être visible par les bénéficiaires'}
            </div>
          )}
        </HomeCard>
      )}
    </>
  )
}

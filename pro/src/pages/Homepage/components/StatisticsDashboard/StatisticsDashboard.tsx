import cn from 'classnames'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUES_STATS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { Panel } from '@/ui-kit/Panel/Panel'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CumulatedViews } from './components/CumulatedViews'
import { CumulatedViewsSkeleton } from './components/CumulatedViewsSkeleton'
import { MostViewedOffers } from './components/MostViewedOffers'
import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  venue: GetVenueResponseModel
}

export const StatisticsDashboard = ({ venue }: StatisticsDashboardProps) => {
  const { isLoading, data: stats } = useSWR(
    [GET_VENUES_STATS_QUERY_KEY, venue.id],
    ([, venueId]) => api.getVenueOffersStats(venueId)
  )

  return (
    <Panel>
      {isLoading ? (
        <CumulatedViewsSkeleton />
      ) : stats?.jsonData.topOffers.length ||
        stats?.jsonData.dailyViews.length ? (
        <div
          className={cn(styles['data-container'], {
            [styles['has-top-offers']]: stats.jsonData.topOffers.length > 0,
          })}
        >
          <CumulatedViews
            dailyViews={stats.jsonData.dailyViews}
            totalViewsLast30Days={stats.jsonData.totalViewsLast30Days}
          />
          {stats.jsonData.topOffers.length > 0 && (
            <MostViewedOffers topOffers={stats.jsonData.topOffers} />
          )}
        </div>
      ) : (
        <div className={styles['no-data']}>
          <SvgIcon
            src={strokeNoBookingIcon}
            alt=""
            className={styles['no-data-icon']}
            width="42"
          />

          {venue.hasNonDraftOffers
            ? 'Les statistiques de consultation de vos offres seront bientôt disponibles.'
            : 'Créez vos premières offres grand public pour être visible par les bénéficiaires'}
        </div>
      )}
    </Panel>
  )
}

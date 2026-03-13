import cn from 'classnames'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUES_STATS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { Panel } from '@/ui-kit/Panel/Panel'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CumulatedViewsSkeleton } from './components/CumulatedViewsSkeleton'
import { MostViewedOffers } from './components/MostViewedOffers'
import { VenueCumulatedViews } from './components/VenueCumulatedViews'
import styles from './StatisticsDashboard.module.scss'

interface VenueStatisticsDashboardProps {
  venue: GetVenueResponseModel
}

export const VenueStatisticsDashboard = ({
  venue,
}: VenueStatisticsDashboardProps) => {
  const { isLoading, data: stats } = useSWR(
    [GET_VENUES_STATS_QUERY_KEY, venue.id],
    ([, venueId]) => api.getVenueOffersStats(venueId)
  )

  return (
    <Panel>
      {isLoading && <CumulatedViewsSkeleton />}
      {!isLoading &&
        (stats?.jsonData.topOffers.length ||
        stats?.jsonData.monthlyViews.length ? (
          <div
            className={cn(styles['data-container'], {
              [styles['has-top-offers']]: stats.jsonData.topOffers.length > 0,
            })}
          >
            <VenueCumulatedViews
              monthlyViews={stats.jsonData.monthlyViews}
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
            {venue.hasOffers
              ? 'Les statistiques de consultation de vos offres seront bientôt disponibles.'
              : 'Créez vos premières offres grand public pour être visible par les bénéficiaires'}
          </div>
        ))}
    </Panel>
  )
}

import cn from 'classnames'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUES_STATS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Card } from '@/ui-kit/Card/Card'

import { CumulatedViews } from './components/CumulatedViews'
import { MostViewedOffers } from './components/MostViewedOffers'
import styles from './StatsCard.module.scss'

interface StatsCardProps {
  venue: GetVenueResponseModel
}

export const StatsCard = ({ venue }: StatsCardProps) => {
  const { data: stats } = useSWR(
    [GET_VENUES_STATS_QUERY_KEY, venue.id],
    ([, venueId]) => apiNew.getVenueOffersStats({ path: { venue_id: venueId } })
  )

  const dailyViews = stats?.jsonData.dailyViews ?? []

  if (!stats || dailyViews.length < 2) {
    return null
  }

  const { topOffers, totalViewsLast30Days } = stats.jsonData

  return (
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
}

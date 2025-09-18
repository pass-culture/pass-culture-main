import cn from 'classnames'
import { format } from 'date-fns'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import { GET_OFFERER_STATISTICS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { Card } from '../../../../components/Card/Card'
import { CumulatedViews } from './components/CumulatedViews'
import { MostViewedOffers } from './components/MostViewedOffers'
import { OfferStats } from './components/OfferStats'
import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  offerer: GetOffererResponseModel
}

export const StatisticsDashboard = ({ offerer }: StatisticsDashboardProps) => {
  const { data: stats, isLoading } = useSWR(
    [GET_OFFERER_STATISTICS_QUERY_KEY, offerer.id],
    ([, offererId]) => api.getOffererStats(offererId)
  )

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['title']}>
          Présence sur l’application pass Culture
        </h2>
      </div>

      {!isLoading && (
        <Card>
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
          {stats?.syncDate ? (
            <div className={styles['sync-date']}>
              Dernière mise à jour :{' '}
              {format(new Date(stats.syncDate), FORMAT_DD_MM_YYYY_HH_mm)}
            </div>
          ) : null}
        </Card>
      )}

      <OfferStats offerer={offerer} className={styles['offer-stats']} />
    </>
  )
}

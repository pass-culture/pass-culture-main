import { format } from 'date-fns'
import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererStatsResponseModel,
} from 'apiClient/v1'
import fullMoreIcon from 'icons/full-more.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'

import { STEP_HOME_STATS_HASH } from '../HomepageBreadcrumb'

import { CumulatedViews } from './CumulatedViews'
import { MostViewedOffers } from './MostViewedOffers'
import styles from './StatisticsDashboard.module.scss'

export interface StatisticsDashboardProps {
  offerer: GetOffererResponseModel
}

export const StatisticsDashboard = ({ offerer }: StatisticsDashboardProps) => {
  const [stats, setStats] = useState<GetOffererStatsResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)

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

  const hasAtLeastOneOffer = Boolean(
    offerer.managedVenues?.some((venue) => venue.hasCreatedOffer)
  )

  return (
    <section className={styles['section']}>
      <div className={styles['header']}>
        <h2 className={styles['title']} id={STEP_HOME_STATS_HASH}>
          Présence sur le pass Culture
        </h2>

        <ButtonLink
          variant={ButtonVariant.PRIMARY}
          link={{
            isExternal: false,
            to: `/offre/creation?structure=${offerer.id}`,
          }}
          icon={fullMoreIcon}
        >
          Créer une offre
        </ButtonLink>
      </div>

      {!isLoading && (
        <div className="h-card">
          <div className="h-card-inner">
            {stats?.jsonData?.topOffers && stats.jsonData.dailyViews ? (
              <div className={styles['data-container']}>
                <MostViewedOffers
                  topOffers={stats.jsonData.topOffers}
                  dailyViews={stats.jsonData.dailyViews}
                />

                <CumulatedViews />
              </div>
            ) : (
              <div className={styles['no-data']}>
                <SvgIcon
                  src={strokeNoBookingIcon}
                  alt=""
                  viewBox="0 0 200 156"
                  className={styles['no-data-icon']}
                  width="42"
                />

                {hasAtLeastOneOffer
                  ? 'Les statistiques de consultation de vos offres seront bientôt disponibles.'
                  : 'Créez vos premières offres grand public pour être visible par les bénéficiaires'}
              </div>
            )}

            <div className={styles['sync-date']}>
              Dernière mise à jour :{' '}
              {stats?.syncDate
                ? format(new Date(stats.syncDate), FORMAT_DD_MM_YYYY_HH_mm)
                : 'N/A'}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

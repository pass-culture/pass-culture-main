import cn from 'classnames'
import { format } from 'date-fns'
import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererStatsResponseModel,
} from 'apiClient/v1'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullMoreIcon from 'icons/full-more.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'

import { Card } from '../Card'

import { CumulatedViews } from './CumulatedViews'
import { MostViewedOffers } from './MostViewedOffers'
import { OfferStats } from './OfferStats'
import styles from './StatisticsDashboard.module.scss'

interface StatisticsDashboardProps {
  offerer: GetOffererResponseModel
}

export const StatisticsDashboard = ({ offerer }: StatisticsDashboardProps) => {
  const [stats, setStats] = useState<GetOffererStatsResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const { currentUser } = useCurrentUser()

  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const createOfferLink = `/offre/creation${!isNewSideBarNavigation ? `?structure=${offerer.id}` : ''}`

  const displayCreateOfferButton =
    (isNewSideBarNavigation && currentUser.isAdmin) || !isNewSideBarNavigation

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
        <h2 className={styles['title']}>Présence sur le pass Culture</h2>

        {displayCreateOfferButton && (
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to={createOfferLink}
            icon={fullMoreIcon}
          >
            Créer une offre
          </ButtonLink>
        )}
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

          <div className={styles['sync-date']}>
            Dernière mise à jour :{' '}
            {stats?.syncDate ? (
              format(new Date(stats.syncDate), FORMAT_DD_MM_YYYY_HH_mm)
            ) : (
              <abbr title="Non applicable">N/A</abbr>
            )}
          </div>
        </Card>
      )}

      <OfferStats offerer={offerer} className={styles['offer-stats']} />
    </>
  )
}

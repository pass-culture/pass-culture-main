import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererV2StatsResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import fullLinkIcon from 'icons/full-link.svg'
import fullShowIcon from 'icons/full-show.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Card } from '../Card'

import styles from './OfferStats.module.scss'

export interface OfferStatsProps {
  offerer: GetOffererResponseModel
  className?: string
}

interface StatBlockProps {
  icon: string
  count: number
  label: string
  link: string
  linkLabel: string
}

const StatBlock = ({ icon, count, label, link, linkLabel }: StatBlockProps) => (
  <div className={styles['stat-block']}>
    <SvgIcon
      width="48"
      src={icon}
      alt=""
      className={styles['stat-block-icon']}
    />

    <div className={styles['stat-block-text']}>
      <p>
        <span className={styles['stat-block-count']}>
          {getOffersCountToDisplay(count)}
        </span>{' '}
        {label}
      </p>
      <ButtonLink
        variant={ButtonVariant.QUATERNARY}
        icon={fullShowIcon}
        link={{ to: link, isExternal: false }}
      >
        {linkLabel}
      </ButtonLink>
    </div>
  </div>
)

export const OfferStats = ({ offerer, className }: OfferStatsProps) => {
  const [stats, setStats] = useState<GetOffererV2StatsResponseModel | null>(
    null
  )
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true)
      const response = await api.getOffererV2Stats(offerer.id)
      setStats(response)
      setIsLoading(false)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStats()
  }, [offerer.id])

  return (
    <Card className={className}>
      <h3 className={styles['title']}>Vos offres publiées</h3>

      <div className={styles['container']}>
        {isLoading || stats === null ? (
          <>
            <div className={styles['skeleton']} />
            <div className={styles['skeleton']} />
          </>
        ) : (
          <>
            <StatBlock
              icon={strokePhoneIcon}
              count={stats.publishedPublicOffers}
              label="à destination du grand public"
              link={`/offres?structure=${offerer.id}&status=active`}
              linkLabel="Voir les offres individuelles publiées"
            />

            <StatBlock
              icon={strokeTeacherIcon}
              count={stats.publishedEducationalOffers}
              label="à destination de groupes scolaires"
              link={`/offres/collectives?structure=${offerer.id}&status=active`}
              linkLabel="Voir les offres collectives publiées"
            />
          </>
        )}
      </div>

      {stats !== null &&
        (stats.pendingEducationalOffers > 0 ||
          stats.pendingPublicOffers > 0) && (
          <div className={styles['pending-offers']}>
            <h3 className={styles['title']}>Vos offres en attente</h3>

            <div className={styles['pending-description']}>
              <p>
                Le contrôle de conformité peut prendre jusqu’à 72 heures. En cas
                de validation, l’offre sera publiée automatiquement.
              </p>

              <ButtonLink
                variant={ButtonVariant.QUATERNARY}
                link={{
                  to: 'https://aide.passculture.app/hc/fr/articles/4412007222289--Acteurs-Culturels-Quelles-sont-les-raisons-possibles-de-refus-de-votre-offre-',
                  isExternal: true,
                }}
                icon={fullLinkIcon}
                svgAlt="Nouvelle fenêtre"
                onClick={() =>
                  logEvent(Events.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ)
                }
              >
                En savoir plus sur les règles de conformité.
              </ButtonLink>
            </div>

            <div className={styles['container']}>
              <StatBlock
                icon={strokePhoneIcon}
                count={stats.pendingPublicOffers}
                label="à destination du grand public"
                link={`/offres?structure=${offerer.id}&status=en-attente`}
                linkLabel="Voir les offres individuelles en attente"
              />

              <StatBlock
                icon={strokeTeacherIcon}
                count={stats.pendingEducationalOffers}
                label="à destination de groupes scolaires"
                link={`/offres/collectives?structure=${offerer.id}&status=en-attente`}
                linkLabel="Voir les offres collectives en attente"
              />
            </div>
          </div>
        )}
    </Card>
  )
}

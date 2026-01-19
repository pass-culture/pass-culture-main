import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFERER_V2_STATS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { Card } from '@/components/Card/Card'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import fullShowIcon from '@/icons/full-show.svg'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant as OldButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { LoadingSkeleton } from './LoadingSkeleton'
import styles from './OfferStats.module.scss'

export interface PublishedOfferStatsProps {
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
      <Button
        as="a"
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        icon={fullShowIcon}
        to={link}
        label={linkLabel}
      />
    </div>
  </div>
)

export const PublishedOfferStats = ({
  offerer,
  className,
}: PublishedOfferStatsProps) => {
  const { logEvent } = useAnalytics()

  const { isLoading, data: stats } = useSWR(
    offerer.id ? [GET_OFFERER_V2_STATS_QUERY_KEY, offerer.id] : null,
    ([, offererId]) => api.getOffererV2Stats(offererId)
  )

  const pendingOfferWording = 'en instruction'

  return (
    <Card className={className}>
      <h3 className={styles['title']}>Vos offres publiées</h3>

      <div className={styles['container']}>
        {isLoading || !stats ? (
          <>
            <LoadingSkeleton />
            <LoadingSkeleton />
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

      {stats !== undefined &&
        (stats.pendingEducationalOffers > 0 ||
          stats.pendingPublicOffers > 0) && (
          <div className={styles['pending-offers']}>
            <h3 className={styles['title']}>
              Vos offres {pendingOfferWording}
            </h3>

            <div className={styles['pending-description']}>
              <p>
                Le contrôle de conformité peut prendre jusqu’à 72 heures. En cas
                de validation, l’offre sera publiée automatiquement.
              </p>

              <ButtonLink
                variant={OldButtonVariant.QUATERNARY}
                to="https://aide.passculture.app/hc/fr/articles/4412007222289--Acteurs-Culturels-Quelles-sont-les-raisons-possibles-de-refus-de-votre-offre-"
                isExternal
                icon={fullLinkIcon}
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
                linkLabel={`Voir les offres individuelles ${pendingOfferWording}`}
              />

              <StatBlock
                icon={strokeTeacherIcon}
                count={stats.pendingEducationalOffers}
                label="à destination de groupes scolaires"
                link={`/offres/collectives?structure=${offerer.id}&status=en-attente`}
                linkLabel={`Voir les offres collectives ${pendingOfferWording}`}
              />
            </div>
          </div>
        )}
    </Card>
  )
}

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { WEBAPP_URL } from 'commons/utils/config'
import { copyTextToClipboard } from 'commons/utils/copyTextToClipboard'
import fullDuplicateIcon from 'icons/full-duplicate.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './PartnerPage.module.scss'

export type PartnerPageIndividualSectionProps = {
  venueId: number
  offererId: number
  venueName: string
  isVisibleInApp: boolean
  isDisplayedInHomepage?: boolean
}

export function PartnerPageIndividualSection({
  venueId,
  venueName,
  offererId,
  isVisibleInApp,
  isDisplayedInHomepage = false,
}: PartnerPageIndividualSectionProps) {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venueId}`
  const logVenueLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK, {
      venueId: venueId,
    })
  }

  const copyVenueLink = async () => {
    await copyTextToClipboard(venuePreviewLink)
    notify.success('Lien copié !')
    logEvent(Events.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK, {
      venueId: venueId,
    })
  }

  return (
    <section className={styles['details']}>
      <div>
        {isDisplayedInHomepage ? (
          <h4 className={styles['details-title']}>Grand public</h4>
        ) : (
          <span className={styles['details-normal']}>
            État de votre page partenaire sur l’application :
          </span>
        )}
        {isVisibleInApp ? (
          <Tag className={styles['tag']} variant={TagVariant.LIGHT_GREEN}>
            Visible
          </Tag>
        ) : (
          <Tag className={styles['tag']} variant={TagVariant.LIGHT_BLUE}>
            Non visible
          </Tag>
        )}
      </div>
      {isDisplayedInHomepage && (
        <p className={styles['details-description']}>
          {isVisibleInApp
            ? 'Votre page partenaire est visible sur l’application pass Culture.'
            : 'Votre page n’est pas visible par les utilisateurs de l’application pass Culture. Vos offres publiées restent cependant visibles et réservables par les bénéficiaires.'}
        </p>
      )}
      {isDisplayedInHomepage && (
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          className={styles['details-link']}
          to={`/structures/${offererId}/lieux/${venueId}/page-partenaire`}
          aria-label={`Gérer la page ${venueName}`}
          icon={fullNextIcon}
          onClick={() =>
            logEvent(Events.CLICKED_PAGE_FOR_APP_HOME, {
              from: location.pathname,
            })
          }
        >
          Gérer votre page pour le grand public
        </ButtonLink>
      )}
      {isVisibleInApp && (
        <>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            icon={fullLinkIcon}
            to={venuePreviewLink}
            isExternal
            opensInNewTab
            className={styles['details-link']}
            onClick={logVenueLinkClick}
          >
            Voir votre page dans l’application
          </ButtonLink>

          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullDuplicateIcon}
            className={styles['details-link']}
            onClick={copyVenueLink}
          >
            Copier le lien de la page
          </Button>
        </>
      )}
    </section>
  )
}

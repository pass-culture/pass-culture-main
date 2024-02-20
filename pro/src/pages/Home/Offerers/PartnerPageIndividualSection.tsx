import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullDuplicateIcon from 'icons/full-duplicate.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { copyTextToClipboard } from 'ui-kit/CopyLink/CopyLink'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { WEBAPP_URL } from 'utils/config'

import styles from './PartnerPage.module.scss'

type PartnerPageIndividualSectionProps = {
  venueId: number
  isVisibleInApp: boolean
  displayTitle?: boolean
}

export function PartnerPageIndividualSection({
  venueId,
  isVisibleInApp,
  displayTitle = false,
}: PartnerPageIndividualSectionProps) {
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venueId}`
  const logVenueLinkClick = () => {
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK, {
      venueId: venueId,
    })
  }

  const copyVenueLink = async () => {
    await copyTextToClipboard(venuePreviewLink)
    notify.success('Lien copié !')
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK, {
      venueId: venueId,
    })
  }

  return (
    <section className={styles['details']}>
      <div>
        {displayTitle ? (
          <h4 className={styles['details-title']}>Grand public</h4>
        ) : (
          <span className={styles['details-normal']}>
            État de votre page partenaire sur l’application :
          </span>
        )}
        {isVisibleInApp ? (
          <Tag variant={TagVariant.LIGHT_GREEN}>Visible</Tag>
        ) : (
          <Tag variant={TagVariant.LIGHT_BLUE}>Non visible</Tag>
        )}
      </div>

      <p className={styles['details-description']}>
        Votre page partenaire est visible sur l’application pass Culture.
      </p>

      <ButtonLink
        variant={ButtonVariant.TERNARY}
        icon={fullLinkIcon}
        link={{
          to: venuePreviewLink,
          isExternal: true,
          target: '_blank',
        }}
        svgAlt="Nouvelle fenêtre"
        className={styles['details-link']}
        onClick={logVenueLinkClick}
      >
        Voir ma page dans l’application
      </ButtonLink>

      <Button
        variant={ButtonVariant.TERNARY}
        icon={fullDuplicateIcon}
        className={styles['details-link']}
        onClick={copyVenueLink}
      >
        Copier le lien de la page
      </Button>
    </section>
  )
}

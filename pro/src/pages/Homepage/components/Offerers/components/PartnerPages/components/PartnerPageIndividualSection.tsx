import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { WEBAPP_URL } from '@/commons/utils/config'
import { copyTextToClipboard } from '@/commons/utils/copyTextToClipboard'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullDuplicateIcon from '@/icons/full-duplicate.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './PartnerPage.module.scss'

export type PartnerPageIndividualSectionProps = {
  venueId: number
  offererId: number
  venueName: string
}

export function PartnerPageIndividualSection({
  venueId,
  venueName,
  offererId,
}: PartnerPageIndividualSectionProps) {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venueId}`
  const logVenueLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK, {
      venueId: venueId,
    })
  }

  const copyVenueLink = async () => {
    await copyTextToClipboard(venuePreviewLink)
    snackBar.success('Lien copié !')
    logEvent(Events.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK, {
      venueId: venueId,
    })
  }

  return (
    <section className={styles['details']}>
      <div>
        <h4 className={styles['details-title']}>Grand public</h4>
      </div>
      <div className={styles['details-link']}>
        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          to={`/structures/${offererId}/lieux/${venueId}/page-partenaire`}
          aria-label={`Gérer la page ${venueName}`}
          icon={fullNextIcon}
          onClick={() =>
            logEvent(Events.CLICKED_PAGE_FOR_APP_HOME, {
              from: location.pathname,
            })
          }
          label="Gérer votre page pour le grand public"
        />
      </div>

      <div className={styles['details-link']}>
        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={fullLinkIcon}
          to={venuePreviewLink}
          isExternal
          opensInNewTab
          onClick={logVenueLinkClick}
          label="Voir votre page dans l’application"
        />
      </div>

      <div className={styles['details-link']}>
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={fullDuplicateIcon}
          onClick={copyVenueLink}
          label="Copier le lien de la page"
        />
      </div>
    </section>
  )
}

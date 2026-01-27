import { type DMSApplicationForEAC, DMSApplicationstatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { getLastCollectiveDmsApplication } from '@/commons/utils/getLastCollectiveDmsApplication'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullInfoIcon from '@/icons/full-info.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './PartnerPage.module.scss'

export type PartnerPageCollectiveSectionProps = {
  collectiveDmsApplications: DMSApplicationForEAC[]
  venueId: number
  offererId: number
  venueName: string
  allowedOnAdage: boolean
  isDisplayedInHomepage?: boolean
}

export function PartnerPageCollectiveSection({
  venueId,
  offererId,
  venueName,
  allowedOnAdage,
  collectiveDmsApplications,
  isDisplayedInHomepage = false,
}: PartnerPageCollectiveSectionProps) {
  const { logEvent } = useAnalytics()

  const lastDmsApplication = getLastCollectiveDmsApplication(
    collectiveDmsApplications
  )

  const logCollectiveHelpLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK, {
      venueId: venueId,
    })
  }

  const logDMSApplicationLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK, {
      venueId: venueId,
    })
  }

  if (allowedOnAdage) {
    return (
      <AdageInformations
        tagText="Référencé dans ADAGE"
        variant={TagVariant.SUCCESS}
        isDisplayedInHomepage={isDisplayedInHomepage}
        description={
          isDisplayedInHomepage
            ? 'Les enseignants voient les offres vitrines et celles que vous adressez à leur établissement sur ADAGE. Complétez vos informations à destination des enseignants pour qu’ils vous contactent !'
            : undefined
        }
        offererId={offererId}
        venueId={venueId}
        venueName={venueName}
      />
    )
  } else if (lastDmsApplication === null) {
    return (
      <AdageInformations
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.DEFAULT}
        isDisplayedInHomepage={isDisplayedInHomepage}
        description="Pour pouvoir adresser des offres aux enseignants, vous devez être référencé dans ADAGE, l’application du ministère de l’Éducation nationale dédiée à l’EAC."
        offererId={offererId}
        venueId={venueId}
        venueName={venueName}
      >
        <div className={styles['details-link']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            icon={fullLinkIcon}
            to="https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage"
            isExternal
            opensInNewTab
            onClick={logDMSApplicationLinkClick}
            label="Déposer un dossier ADAGE"
          />
        </div>

        <div className={styles['details-link']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullInfoIcon}
            to="https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires"
            isExternal
            opensInNewTab
            onClick={logCollectiveHelpLinkClick}
            label="En savoir plus sur le pass Culture à destination des scolaires"
          />
        </div>
      </AdageInformations>
    )
  } else if (
    lastDmsApplication.state === DMSApplicationstatus.REFUSE ||
    lastDmsApplication.state === DMSApplicationstatus.SANS_SUITE
  ) {
    return (
      <AdageInformations
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.ERROR}
        isDisplayedInHomepage={isDisplayedInHomepage}
        description="Pour pouvoir adresser des offres aux enseignants, vous devez être
        référencé dans ADAGE, l’application du ministère de l’Éducation
        nationale dédiée à l’EAC."
        offererId={offererId}
        venueId={venueId}
        venueName={venueName}
      />
    )
  }
  // Last case :
  // (lastDmsApplication?.state === DMSApplicationstatus.ACCEPTE && !hasAdageId) ||
  // lastDmsApplication?.state === DMSApplicationstatus.EN_CONSTRUCTION ||
  // lastDmsApplication?.state === DMSApplicationstatus.EN_INSTRUCTION)
  return (
    <AdageInformations
      tagText="Référencement en cours"
      variant={TagVariant.WARNING}
      isDisplayedInHomepage={isDisplayedInHomepage}
      description="Votre démarche de référencement est en cours de traitement par ADAGE."
      offererId={offererId}
      venueId={venueId}
      venueName={venueName}
    >
      <div className={styles['details-link']}>
        <Button
          as="a"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullInfoIcon}
          to="https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires"
          isExternal
          opensInNewTab
          onClick={logCollectiveHelpLinkClick}
          label="En savoir plus sur le pass Culture à destination des scolaires"
        />
      </div>
    </AdageInformations>
  )
}

type AdageInformationsProps = {
  children?: React.ReactNode
  variant: TagVariant
  tagText: string
  isDisplayedInHomepage: boolean
  description?: string
  offererId: number
  venueId: number
  venueName: string
}

function AdageInformations({
  children,
  tagText,
  variant,
  isDisplayedInHomepage,
  description,
  offererId,
  venueId,
  venueName,
}: AdageInformationsProps) {
  const { logEvent } = useAnalytics()
  return (
    <section className={styles['details']}>
      <div>
        {isDisplayedInHomepage ? (
          <h4 className={styles['details-title']}>Enseignants</h4>
        ) : (
          <span className={styles['details-normal']}>
            État auprès des enseignants&nbsp;:
          </span>
        )}
        <div className={styles['tag']}>
          <Tag label={tagText} variant={variant} />
        </div>
      </div>
      {description && (
        <p className={styles['details-description']}>{description}</p>
      )}
      {isDisplayedInHomepage && (
        <div className={styles['details-link']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            to={`/structures/${offererId}/lieux/${venueId}/collectif`}
            aria-label={`Gérer la page pour les enseignants ${venueName}`}
            icon={fullNextIcon}
            onClick={() =>
              logEvent(Events.CLICKED_PAGE_FOR_ADAGE_HOME, {
                from: location.pathname,
              })
            }
            label="Gérer votre page pour les enseignants"
          />
        </div>
      )}
      {children}
    </section>
  )
}

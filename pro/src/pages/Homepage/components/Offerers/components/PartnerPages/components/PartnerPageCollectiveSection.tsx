import { DMSApplicationstatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './PartnerPage.module.scss'

interface PartnerPageCollectiveSectionProps {
  isDisplayedInHomepage?: boolean
}

export const PartnerPageCollectiveSection = ({
  isDisplayedInHomepage = false,
}: Readonly<PartnerPageCollectiveSectionProps>) => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const { logEvent } = useAnalytics()

  const logCollectiveHelpLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK, {
      venueId: selectedPartnerVenue.id,
    })
  }

  const logDMSApplicationLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK, {
      venueId: selectedPartnerVenue.id,
    })
  }

  if (selectedPartnerVenue.allowedOnAdage) {
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
        venueName={selectedPartnerVenue.name}
      />
    )
  }

  if (selectedPartnerVenue.lastCollectiveDmsApplication === null) {
    return (
      <AdageInformations
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.DEFAULT}
        isDisplayedInHomepage={isDisplayedInHomepage}
        description="Pour pouvoir adresser des offres aux enseignants, vous devez être référencé dans ADAGE, l’application du ministère de l’Éducation nationale dédiée à l’EAC."
        venueName={selectedPartnerVenue.name}
      >
        <div className={styles['details-link']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
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

  if (
    selectedPartnerVenue.lastCollectiveDmsApplication.state ===
      DMSApplicationstatus.REFUSE ||
    selectedPartnerVenue.lastCollectiveDmsApplication.state ===
      DMSApplicationstatus.SANS_SUITE
  ) {
    return (
      <AdageInformations
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.ERROR}
        isDisplayedInHomepage={isDisplayedInHomepage}
        description="Pour pouvoir adresser des offres aux enseignants, vous devez être
        référencé dans ADAGE, l’application du ministère de l’Éducation
        nationale dédiée à l’EAC."
        venueName={selectedPartnerVenue.name}
      />
    )
  }

  return (
    <AdageInformations
      tagText="Référencement en cours"
      variant={TagVariant.WARNING}
      isDisplayedInHomepage={isDisplayedInHomepage}
      description="Votre démarche de référencement est en cours de traitement par ADAGE."
      venueName={selectedPartnerVenue.name}
    >
      <div className={styles['details-link']}>
        <Button
          as="a"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
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
  venueName: string
}

function AdageInformations({
  children,
  tagText,
  variant,
  isDisplayedInHomepage,
  description,
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
            to={`/partenaire/page-collective`}
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

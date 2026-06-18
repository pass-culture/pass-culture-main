import { DMSApplicationstatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Link } from '@/design-system/Link/Link'
import { LinkColor } from '@/design-system/Link/types'
import { TagVariant } from '@/design-system/Tag/Tag'

import { AdageSection } from './AdageSection'
import styles from './PartnerPageCollectiveSection.module.scss'

export const PartnerPageCollectiveSection = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const { logEvent } = useAnalytics()

  const logCollectiveHelpLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK)
  }

  const logDMSApplicationLinkClick = () => {
    logEvent(Events.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK)
  }

  if (selectedPartnerVenue.allowedOnAdage) {
    return (
      <AdageSection
        tagText="Référencé dans ADAGE"
        variant={TagVariant.SUCCESS}
      />
    )
  }

  if (selectedPartnerVenue.lastCollectiveDmsApplication === null) {
    return (
      <AdageSection
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.DEFAULT}
        description={
          <p>
            Pour pouvoir adresser des offres aux enseignants, vous devez être
            référencé sur ADAGE, l'application du ministère de l'Education
            nationale et de la Jeunesse dédiée à l'EAC. Si vous souhaitez en
            savoir plus sur le pass Culture à destination des scolaires, vous
            pouvez{' '}
            <Link
              color={LinkColor.NEUTRAL}
              to="https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires"
              isExternalLink
              onClick={logCollectiveHelpLinkClick}
              shouldOpenNewTab
              label="Consulter notre page pass Culture pour le scolaires"
            />
          </p>
        }
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
      </AdageSection>
    )
  }

  if (
    selectedPartnerVenue.lastCollectiveDmsApplication.state ===
      DMSApplicationstatus.REFUSE ||
    selectedPartnerVenue.lastCollectiveDmsApplication.state ===
      DMSApplicationstatus.SANS_SUITE
  ) {
    return (
      <AdageSection
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.ERROR}
        description={
          <p>
            Pour pouvoir adresser des offres aux enseignants, vous devez être
            référencé sur ADAGE, l'application du ministère de l'Education
            nationale et de la Jeunesse dédiée à l'EAC. Si vous souhaitez en
            savoir plus sur le pass Culture à destination des scolaires, vous
            pouvez{' '}
            <Link
              color={LinkColor.NEUTRAL}
              to="https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires"
              isExternalLink
              onClick={logCollectiveHelpLinkClick}
              shouldOpenNewTab
              label="Consulter notre page pass Culture pour le scolaires"
            />
          </p>
        }
      />
    )
  }

  return (
    <AdageSection
      tagText="Référencement en cours"
      variant={TagVariant.WARNING}
      description={
        <p>
          Votre démarche de référencement est en cours de traitement par ADAGE.
        </p>
      }
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
    </AdageSection>
  )
}

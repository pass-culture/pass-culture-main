import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullInfoIcon from 'icons/full-info.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import styles from './PartnerPage.module.scss'

export function PartnerPageCollectiveSection({
  collectiveDmsApplications,
  venueId,
  hasAdageId,
}: {
  collectiveDmsApplications: DMSApplicationForEAC[]
  venueId: number
  hasAdageId: boolean
}) {
  const { logEvent } = useAnalytics()

  const lastDmsApplication = getLastCollectiveDmsApplication(
    collectiveDmsApplications
  )

  const logCollectiveHelpLinkClick = () => {
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK, {
      venueId: venueId,
    })
  }

  const logDMSApplicationLinkClick = () => {
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK, {
      venueId: venueId,
    })
  }

  if (
    lastDmsApplication?.state === DMSApplicationstatus.ACCEPTE ||
    hasAdageId
  ) {
    return (
      <section className={styles['details']}>
        <div>
          <h4 className={styles['details-title']}>Enseignants</h4>
          <Tag variant={TagVariant.LIGHT_GREEN}>Référencé sur ADAGE</Tag>
        </div>

        <p className={styles['details-description']}>
          Les enseignants voient les offres vitrines et celles que vous adressez
          à leur établissement sur ADAGE. Complétez vos informations à
          destination des enseignants pour qu’ils vous contactent !
        </p>
      </section>
    )
  } else if (lastDmsApplication === null) {
    return (
      <section className={styles['details']}>
        <div>
          <h4 className={styles['details-title']}>Enseignants</h4>
          <Tag variant={TagVariant.LIGHT_BLUE}>Non référencé sur ADAGE</Tag>
        </div>

        <p className={styles['details-description']}>
          Pour pouvoir adresser des offres aux enseignants, vous devez être
          référencé sur ADAGE, l’application du ministère de l’Education
          nationale et de la Jeunesse dédiée à l’EAC.
        </p>

        <ButtonLink
          variant={ButtonVariant.TERNARY}
          icon={fullLinkIcon}
          link={{
            to: 'https://www.demarches-simplifiees.fr/commencer/demande-de-referencement-sur-adage',
            isExternal: true,
            target: '_blank',
            rel: 'noopener noreferrer',
          }}
          svgAlt="Nouvelle fenêtre"
          className={styles['details-link']}
          onClick={logDMSApplicationLinkClick}
        >
          Faire une demande de référencement ADAGE
        </ButtonLink>

        <ButtonLink
          variant={ButtonVariant.TERNARY}
          icon={fullInfoIcon}
          link={{
            to: 'https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires',
            isExternal: true,
            target: '_blank',
            rel: 'noopener noreferrer',
          }}
          svgAlt="Nouvelle fenêtre"
          className={styles['details-link']}
          onClick={logCollectiveHelpLinkClick}
        >
          En savoir plus sur le pass Culture à destination des scolaires
        </ButtonLink>
      </section>
    )
  } else if (
    lastDmsApplication?.state === DMSApplicationstatus.REFUSE ||
    lastDmsApplication?.state === DMSApplicationstatus.SANS_SUITE
  ) {
    return (
      <section className={styles['details']}>
        <div>
          <h4 className={styles['details-title']}>Enseignants</h4>
          <Tag variant={TagVariant.LIGHT_BLUE}>Non référencé sur ADAGE</Tag>
        </div>

        <p className={styles['details-description']}>
          Pour pouvoir adresser des offres aux enseignants, vous devez être
          référencé sur ADAGE, l’application du ministère de l’Education
          nationale et de la Jeunesse dédiée à l’EAC.
        </p>
      </section>
    )
  }
  // Last case :
  // lastDmsApplication?.state === DMSApplicationstatus.EN_CONSTRUCTION ||
  // lastDmsApplication?.state === DMSApplicationstatus.EN_INSTRUCTION)
  return (
    <section className={styles['details']}>
      <div>
        <h4 className={styles['details-title']}>Enseignants</h4>
        <Tag variant={TagVariant.LIGHT_YELLOWN}>Référencement en cours</Tag>
      </div>

      <p className={styles['details-description']}>
        Votre démarche de référencement est en cours de traitement par ADAGE.
      </p>

      <ButtonLink
        variant={ButtonVariant.TERNARY}
        icon={fullInfoIcon}
        link={{
          to: 'https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires',
          isExternal: true,
          target: '_blank',
          rel: 'noopener noreferrer',
        }}
        svgAlt="Nouvelle fenêtre"
        className={styles['details-link']}
        onClick={logCollectiveHelpLinkClick}
      >
        En savoir plus sur le pass Culture à destination des scolaires
      </ButtonLink>
    </section>
  )
}

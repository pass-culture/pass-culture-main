// Fichier de mapping enum => string. Pas besoin de tester
/* istanbul ignore file */

import type { BannerLink } from 'design-system/Banner/Banner'

import {
  ContentMessageSignupSimulation,
  EligibilityDocuments,
} from 'apiClient/v1'
import styles from './SimulatorResults.module.scss'

export const getDocumentCardContent = (
  document: EligibilityDocuments
): { title: string; description: string | JSX.Element } => {
  switch (document) {
    case EligibilityDocuments.WEBSITE:
      return {
        title: 'Un site internet ou page de réseau social',
        description: 'Pour présenter votre activité',
      }
    case EligibilityDocuments.RESUME_OR_PORTFOLIO:
      return {
        title: 'CV et/ou portfolio',
        description: 'Pour présenter vos expériences passées',
      }
    case EligibilityDocuments.DIPLOMAS:
      return {
        title: 'Diplôme(s)',
        description: 'Lié(s) à l’activité que vous souhaitez proposer',
      }
    case EligibilityDocuments.SOUND_DESIGN_DIPLOMAS:
      return {
        title: 'Diplôme et/ou attestation dans les métiers du son',
        description: 'Pour valider votre expertise technique',
      }
    case EligibilityDocuments.PRICES:
      return {
        title: 'Grille tarifaire',
        description: 'Document listant le prix standard de vos prestations',
      }
    case EligibilityDocuments.SHOP_PICTURES:
      return {
        title: 'Photos du point de vente',
        description: 'Inclure des rayons de livres et la devanture',
      }
    case EligibilityDocuments.SOUND_STUDIO_PICTURES:
      return {
        title: 'Photos des locaux et du matériel',
        description:
          'Photos intérieures et extérieures avec le nom de l’enseigne visible',
      }
    case EligibilityDocuments.CRIMINAL_RECORDS:
      return {
        title: 'Extrait de casier judiciaire (bulletin n°3)',
        description: (
          <>
            Vous pouvez vous le procurez sur le{' '}
            <a
              className={styles['link']}
              rel="noreferrer"
              target="_blank"
              href="https://casier-judiciaire.justice.gouv.fr/"
            >
              site du gouvernement.
            </a>
          </>
        ),
      }
    case EligibilityDocuments.DESCRIPTION:
      return {
        title: 'Une description détaillée de vos offres',
        description: 'Pour expliquer ce que vous souhaitez proposer',
      }
  }
}

export const getAlertContent = (
  message: ContentMessageSignupSimulation
): { title: string; description?: JSX.Element; link?: BannerLink[] } => {
  switch (message) {
    case ContentMessageSignupSimulation.COLLECTIVE:
      return {
        title:
          'En plus de ces éléments, il vous sera demandé lors de votre dépôt de dossier ADAGE : ',
        description: (
          <ul className={styles['list']}>
            <li>
              Un descriptif de votre projet professionnel artistique et culturel
            </li>
            <li>Vos motivations à proposer des offres aux groupes scolaires</li>
          </ul>
        ),
      }

    case ContentMessageSignupSimulation.BOOKSTORE:
      return {
        title:
          "Vous devez obligatoirement disposer d'un point de vente physique pour proposer vos offres de livres sur le pass Culture.",
      }

    case ContentMessageSignupSimulation.UNUSUAL_APE_CODE:
      return {
        title:
          'Attention, seules certaines activités fixées par arrêté sont éligibles au pass Culture',
        link: [
          {
            label: 'Voir les activités éligibles',
            href: 'https://aide.passculture.app/hc/fr/articles/4412007184017--Acteurs-Culturels-Comment-savoir-si-votre-structure-est-%C3%A9ligible-au-pass-Culture',
            isExternal: true,
            type: 'link',
          },
        ],
      }
  }
}

import React from 'react'

import { OfferStatus, WithdrawalTypeEnum } from 'apiClient/v1'
import AccessibilitySummarySection from 'components/AccessibilitySummarySection'
import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WITHDRAWAL_TYPE_LABELS, OFFER_WIZARD_MODE } from 'core/Offers'
import { AccessiblityEnum, IAccessibiltyFormValues } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

import humanizeDelay from './utils'

export interface IOfferSectionProps {
  id: string
  nonHumanizedId: number
  name: string
  description: string
  categoryName: string
  subCategoryName: string
  subcategoryId: string

  musicTypeName?: string
  musicSubTypeName?: string
  showTypeName?: string
  showSubTypeName?: string

  accessibility: IAccessibiltyFormValues

  isDuo: boolean
  author: string
  stageDirector: string
  speaker: string
  visa: string
  performer: string
  isbn: string
  durationMinutes: string
  url: string
  externalTicketOfficeUrl: string

  venueName: string
  venuePublicName: string
  isVenueVirtual: boolean
  offererName: string
  bookingEmail: string
  withdrawalDetails: string
  withdrawalType: WithdrawalTypeEnum | null
  withdrawalDelay: number | null
  status: OfferStatus
}

interface IOfferSummaryProps {
  offer: IOfferSectionProps
  conditionalFields: string[]
}

const OfferSummary = ({
  offer,
  conditionalFields,
}: IOfferSummaryProps): JSX.Element => {
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const mode = useOfferWizardMode()
  const informationsUrls = isOfferFormV3
    ? {
        creation: `/offre/${offer.id}/v3/creation/individuelle/informations`,
        edition: `/offre/${offer.id}/v3/individuelle/informations`,
      }
    : {
        creation: `/offre/${offer.id}/individuel/creation`,
        edition: `/offre/${offer.id}/individuel/edition`,
      }
  const editLink =
    mode === OFFER_WIZARD_MODE.CREATION
      ? informationsUrls.creation
      : informationsUrls.edition
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.DETAILS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offer.id,
      isEdition: mode === OFFER_WIZARD_MODE.EDITION,
    })
  }

  return (
    <SummaryLayout.Section
      title="Détails de l'offre"
      editLink={editLink}
      onLinkClick={logEditEvent}
    >
      <SummaryLayout.SubSection title="Type d'offre">
        <SummaryLayout.Row title="Catégorie" description={offer.categoryName} />
        <SummaryLayout.Row
          title="Sous-catégorie"
          description={offer.subCategoryName}
        />

        {conditionalFields.includes('musicType') && (
          <SummaryLayout.Row
            title="Genre musical"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offer.musicTypeName || '-'
            }
          />
        )}
        {offer.musicSubTypeName && (
          <SummaryLayout.Row
            title="Sous-genre"
            description={offer.musicSubTypeName}
          />
        )}
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('showType') && (
            <SummaryLayout.Row
              title="Type de spéctacle"
              description={
                /* istanbul ignore next: DEBT, TO FIX */
                offer.showTypeName || '-'
              }
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          offer.showSubTypeName && (
            <SummaryLayout.Row
              title="Sous-type"
              description={offer.showSubTypeName}
            />
          )
        }
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations artistiques">
        <SummaryLayout.Row title="Titre de l'offre" description={offer.name} />
        <SummaryLayout.Row
          title="Description"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offer.description || ' - '
          }
        />

        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('speaker') && (
            <SummaryLayout.Row
              title="Intervenant"
              description={offer.speaker}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('author') && (
            <SummaryLayout.Row title="Auteur" description={offer.author} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('visa') && (
            <SummaryLayout.Row
              title="Visa d’exploitation"
              description={offer.visa}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('isbn') && (
            <SummaryLayout.Row title="ISBN" description={offer.isbn} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('stageDirector') && (
            <SummaryLayout.Row
              title="Metteur en scène"
              description={offer.stageDirector}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('performer') && (
            <SummaryLayout.Row
              title="Interprète"
              description={offer.performer}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('durationMinutes') && (
            <SummaryLayout.Row
              title="Durée"
              description={
                offer.durationMinutes ? `${offer.durationMinutes} min` : '-'
              }
            />
          )
        }
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations pratiques">
        <SummaryLayout.Row title="Structure" description={offer.offererName} />
        <SummaryLayout.Row
          title="Lieu"
          description={
            /* istanbul ignore next: DEBT, TO FIX */ offer.venuePublicName ||
            offer.venueName
          }
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          offer.withdrawalType && (
            <SummaryLayout.Row
              title="Comment les billets, places seront-ils transmis ?"
              description={OFFER_WITHDRAWAL_TYPE_LABELS[offer.withdrawalType]}
            />
          )
        }

        {
          /* istanbul ignore next: DEBT, TO FIX */
          offer.withdrawalDelay && (
            <SummaryLayout.Row
              title="Heure de retrait"
              description={`${humanizeDelay(
                offer.withdrawalDelay
              )} avant le début de l'évènement`}
            />
          )
        }

        <SummaryLayout.Row
          title="Informations de retrait"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offer.withdrawalDetails || ' - '
          }
        />

        {conditionalFields.includes('url') && (
          <SummaryLayout.Row
            title="URL d’accès à l’offre"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offer.url || ' - '
            }
          />
        )}
      </SummaryLayout.SubSection>

      <AccessibilitySummarySection
        noDisabilityCompliance={offer.accessibility[AccessiblityEnum.NONE]}
        visualDisabilityCompliant={offer.accessibility[AccessiblityEnum.VISUAL]}
        mentalDisabilityCompliant={offer.accessibility[AccessiblityEnum.MENTAL]}
        motorDisabilityCompliant={offer.accessibility[AccessiblityEnum.MOTOR]}
        audioDisabilityCompliant={offer.accessibility[AccessiblityEnum.AUDIO]}
      />

      {conditionalFields.includes('isDuo') && (
        <SummaryLayout.SubSection title="Autres caractéristiques">
          <SummaryLayout.Row
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offer.isDuo === true
                ? 'Accepter les réservations "Duo"'
                : 'Refuser les réservations "Duo"'
            }
          />
        </SummaryLayout.SubSection>
      )}

      <SummaryLayout.SubSection title="Lien pour le grand public">
        <SummaryLayout.Row
          title="URL de votre site ou billeterie"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offer.externalTicketOfficeUrl || ' - '
          }
        />
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Notifications des réservations">
        <SummaryLayout.Row
          title="E-mail auquel envoyer les notifications"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offer.bookingEmail || ' - '
          }
        />
      </SummaryLayout.SubSection>
    </SummaryLayout.Section>
  )
}

export default OfferSummary

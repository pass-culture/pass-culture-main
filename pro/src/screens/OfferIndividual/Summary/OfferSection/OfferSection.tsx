import React from 'react'

import AccessibilitySummarySection from 'components/AccessibilitySummarySection'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { SummaryLayout } from 'components/SummaryLayout'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WITHDRAWAL_TYPE_LABELS, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { AccessiblityEnum } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

import { serializeOfferSectionData } from './serializer'
import humanizeDelay from './utils'

interface IOfferSummaryProps {
  offer: IOfferIndividual
  conditionalFields: string[]
}

const OfferSummary = ({
  conditionalFields,
  offer,
}: IOfferSummaryProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()
  const { categories, subCategories } = useOfferIndividualContext()
  const offerData = serializeOfferSectionData(offer, categories, subCategories)
  const isPriceCategoriesActive = useActiveFeature(
    'WIP_ENABLE_MULTI_PRICE_STOCKS'
  )

  const editLink = getOfferIndividualUrl({
    offerId: offerData.nonHumanizedId,
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode,
  })

  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerData.id,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
    })
  }

  return (
    <SummaryLayout.Section
      title="Détails de l’offre"
      editLink={editLink}
      onLinkClick={logEditEvent}
      aria-label="Modifier détails de l’offre"
    >
      <SummaryLayout.SubSection title="Type d’offre">
        <SummaryLayout.Row
          title="Catégorie"
          description={offerData.categoryName}
        />
        <SummaryLayout.Row
          title="Sous-catégorie"
          description={offerData.subCategoryName}
        />

        {conditionalFields.includes('musicType') && (
          <SummaryLayout.Row
            title="Genre musical"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.musicTypeName || '-'
            }
          />
        )}
        {offerData.musicSubTypeName && (
          <SummaryLayout.Row
            title="Sous-genre"
            description={offerData.musicSubTypeName}
          />
        )}
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('showType') && (
            <SummaryLayout.Row
              title="Type de spéctacle"
              description={
                /* istanbul ignore next: DEBT, TO FIX */
                offerData.showTypeName || '-'
              }
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          offerData.showSubTypeName && (
            <SummaryLayout.Row
              title="Sous-type"
              description={offerData.showSubTypeName}
            />
          )
        }
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations artistiques">
        <SummaryLayout.Row
          title="Titre de l’offre"
          description={offerData.name}
        />
        <SummaryLayout.Row
          title="Description"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.description || ' - '
          }
        />

        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('speaker') && (
            <SummaryLayout.Row
              title="Intervenant"
              description={offerData.speaker}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('author') && (
            <SummaryLayout.Row title="Auteur" description={offerData.author} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('visa') && (
            <SummaryLayout.Row
              title="Visa d’exploitation"
              description={offerData.visa}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('isbn') && (
            <SummaryLayout.Row title="ISBN" description={offerData.isbn} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('stageDirector') && (
            <SummaryLayout.Row
              title="Metteur en scène"
              description={offerData.stageDirector}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('performer') && (
            <SummaryLayout.Row
              title="Interprète"
              description={offerData.performer}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('durationMinutes') && (
            <SummaryLayout.Row
              title="Durée"
              description={
                offerData.durationMinutes
                  ? `${offerData.durationMinutes} min`
                  : '-'
              }
            />
          )
        }
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Informations pratiques">
        <SummaryLayout.Row
          title="Structure"
          description={offerData.offererName}
        />
        <SummaryLayout.Row
          title="Lieu"
          description={
            /* istanbul ignore next: DEBT, TO FIX */ offerData.venuePublicName ||
            offerData.venueName
          }
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          offerData.withdrawalType && (
            <SummaryLayout.Row
              title="Comment les billets, places seront-ils transmis ?"
              description={
                OFFER_WITHDRAWAL_TYPE_LABELS[offerData.withdrawalType]
              }
            />
          )
        }

        {
          /* istanbul ignore next: DEBT, TO FIX */
          offerData.withdrawalDelay && (
            <SummaryLayout.Row
              title="Heure de retrait"
              description={`${humanizeDelay(
                offerData.withdrawalDelay
              )} avant le début de l’évènement`}
            />
          )
        }

        <SummaryLayout.Row
          title="Informations de retrait"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.withdrawalDetails || ' - '
          }
        />

        {conditionalFields.includes('url') && (
          <SummaryLayout.Row
            title="URL d’accès à l’offre"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.url || ' - '
            }
          />
        )}
      </SummaryLayout.SubSection>

      <AccessibilitySummarySection
        noDisabilityCompliance={offerData.accessibility[AccessiblityEnum.NONE]}
        visualDisabilityCompliant={
          offerData.accessibility[AccessiblityEnum.VISUAL]
        }
        mentalDisabilityCompliant={
          offerData.accessibility[AccessiblityEnum.MENTAL]
        }
        motorDisabilityCompliant={
          offerData.accessibility[AccessiblityEnum.MOTOR]
        }
        audioDisabilityCompliant={
          offerData.accessibility[AccessiblityEnum.AUDIO]
        }
      />

      {!isPriceCategoriesActive && conditionalFields.includes('isDuo') && (
        <SummaryLayout.SubSection title="Autres caractéristiques">
          <SummaryLayout.Row
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.isDuo === true
                ? 'Accepter les réservations "Duo"'
                : 'Refuser les réservations "Duo"'
            }
          />
        </SummaryLayout.SubSection>
      )}

      <SummaryLayout.SubSection title="Lien pour le grand public">
        <SummaryLayout.Row
          title="URL de votre site ou billetterie"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.externalTicketOfficeUrl || ' - '
          }
        />
      </SummaryLayout.SubSection>

      <SummaryLayout.SubSection title="Notifications des réservations">
        <SummaryLayout.Row
          title="E-mail auquel envoyer les notifications"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.bookingEmail || ' - '
          }
        />
      </SummaryLayout.SubSection>
    </SummaryLayout.Section>
  )
}

export default OfferSummary

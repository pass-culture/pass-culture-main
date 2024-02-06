import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import AccessibilitySummarySection from 'components/AccessibilitySummarySection'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { AccessiblityEnum } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import Spinner from 'ui-kit/Spinner/Spinner'

import { OfferSectionData, serializeOfferSectionData } from './serializer'
import humanizeDelay from './utils'

interface OfferSummaryProps {
  offer: IndividualOffer
  conditionalFields: string[]
}

const OfferSummary = ({
  conditionalFields,
  offer,
}: OfferSummaryProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )

  const [offerData, setOfferData] = useState<OfferSectionData>()
  useEffect(() => {
    const updateOfferData = async () => {
      let musicTypes
      if (offer.gtl_id) {
        musicTypes = await api.getAllMusicTypes()
      }
      const data = serializeOfferSectionData(
        offer,
        categories,
        subCategories,
        musicTypes
      )
      setOfferData(data)
    }
    void updateOfferData()
  }, [offer])

  const editLink = getIndividualOfferUrl({
    offerId: offerData?.id,
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
  })

  if (!offerData) {
    return <Spinner />
  }

  return (
    <SummarySection
      title="Détails de l’offre"
      editLink={editLink}
      aria-label="Modifier les détails de l’offre"
    >
      <SummarySubSection title="Type d’offre">
        <SummaryRow title="Catégorie" description={offerData.categoryName} />
        <SummaryRow
          title="Sous-catégorie"
          description={offerData.subCategoryName}
        />

        {conditionalFields.includes('musicType') && (
          <SummaryRow
            title="Genre musical"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.musicTypeName || '-'
            }
          />
        )}
        {offerData.gtl_id && (
          <SummaryRow title="gtl_id" description={offerData.gtl_id} />
        )}
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('showType') && (
            <SummaryRow
              title="Type de spectacle"
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
            <SummaryRow
              title="Sous-type"
              description={offerData.showSubTypeName}
            />
          )
        }
      </SummarySubSection>

      <SummarySubSection title="Informations artistiques">
        <SummaryRow title="Titre de l’offre" description={offerData.name} />
        <SummaryRow
          title="Description"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.description || ' - '
          }
        />

        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('speaker') && (
            <SummaryRow title="Intervenant" description={offerData.speaker} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('author') && (
            <SummaryRow title="Auteur" description={offerData.author} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('visa') && (
            <SummaryRow
              title="Visa d’exploitation"
              description={offerData.visa}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('ean') && (
            <SummaryRow title="EAN-13" description={offerData.ean} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('stageDirector') && (
            <SummaryRow
              title="Metteur en scène"
              description={offerData.stageDirector}
            />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('performer') && (
            <SummaryRow title="Interprète" description={offerData.performer} />
          )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          conditionalFields.includes('durationMinutes') && (
            <SummaryRow
              title="Durée"
              description={
                offerData.durationMinutes
                  ? `${offerData.durationMinutes} min`
                  : '-'
              }
            />
          )
        }
      </SummarySubSection>

      <SummarySubSection title="Informations pratiques">
        <SummaryRow title="Structure" description={offerData.offererName} />
        <SummaryRow
          title="Lieu"
          description={
            /* istanbul ignore next: DEBT, TO FIX */ offerData.venuePublicName ||
            offerData.venueName
          }
        />

        <SummaryRow
          title="Informations de retrait"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.withdrawalDetails || ' - '
          }
        />

        {
          /* istanbul ignore next: DEBT, TO FIX */
          offerData.withdrawalType && (
            <SummaryRow
              title="Précisez la façon dont vous distribuerez les billets"
              description={
                OFFER_WITHDRAWAL_TYPE_LABELS[offerData.withdrawalType]
              }
            />
          )
        }

        {
          /* istanbul ignore next: DEBT, TO FIX */
          offerData.withdrawalDelay && (
            <SummaryRow
              title="Heure de retrait"
              description={`${humanizeDelay(
                offerData.withdrawalDelay
              )} avant le début de l’évènement`}
            />
          )
        }

        {isBookingContactEnabled && offerData.bookingContact && (
          <SummaryRow
            title="Email de contact"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.bookingContact || ' - '
            }
          />
        )}

        {conditionalFields.includes('url') && (
          <SummaryRow
            title="URL d’accès à l’offre"
            description={
              /* istanbul ignore next: DEBT, TO FIX */
              offerData.url || ' - '
            }
          />
        )}
      </SummarySubSection>

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

      <SummarySubSection title="Lien pour le grand public">
        <SummaryRow
          title="URL de votre site ou billetterie"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.externalTicketOfficeUrl || ' - '
          }
        />
      </SummarySubSection>

      <SummarySubSection title="Notifications des réservations">
        <SummaryRow
          title="Email auquel envoyer les notifications"
          description={
            /* istanbul ignore next: DEBT, TO FIX */
            offerData.bookingEmail || ' - '
          }
        />
      </SummarySubSection>
    </SummarySection>
  )
}

export default OfferSummary

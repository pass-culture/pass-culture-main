import { useLocation } from 'react-router'
import { computeAddressDisplayName } from 'repository/venuesService'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { getDelayToFrenchText } from '@/commons/utils/date'
import { AccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { Markdown } from '@/components/Markdown/Markdown'
import {
  type Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import { ARTISTIC_INFORMATION_FIELDS } from '@/pages/IndividualOffer/IndividualOfferDetails/components/DetailsForm/DetailsSubForm/DetailsSubForm'
import { serializeOfferSectionData } from '@/pages/IndividualOfferSummary/commons/serializer'

interface OfferSummaryProps {
  offer: GetIndividualOfferWithAddressResponseModel
  conditionalFields: string[]
}

export const OfferSection = ({
  conditionalFields,
  offer,
}: OfferSummaryProps): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { categories, subCategories } = useIndividualOfferContext()

  const { musicTypes } = useMusicTypes()

  const offerData = serializeOfferSectionData(
    offer,
    categories,
    subCategories,
    musicTypes
  )

  const offerTypeDescriptions: Description[] = [
    { title: 'Catégorie', text: offerData.categoryName },
    { title: 'Sous-catégorie', text: offerData.subCategoryName },
  ]

  const aboutDescriptions: Description[] = [
    {
      title: 'Structure',
      text: offerData.venuePublicName,
    },
    { title: 'Titre de l’offre', text: offerData.name },
    {
      title: 'Description',
      text: !offerData.description ? (
        '-'
      ) : (
        <Markdown markdownText={offerData.description} />
      ),
    },
  ].concat(
    offer.isDigital
      ? {
          title: 'URL d’accès à l’offre',
          text: offer.url || ' - ',
        }
      : []
  )

  const artisticInfoDescriptions: Description[] = []

  if (conditionalFields.includes('musicType')) {
    artisticInfoDescriptions.push({
      title: 'Genre musical',
      text: offerData.musicTypeName || '-',
    })
  }
  if (conditionalFields.includes('showType')) {
    artisticInfoDescriptions.push({
      title: 'Type de spectacle',
      text: offerData.showTypeName || '-',
    })
  }
  if (offerData.showSubTypeName) {
    artisticInfoDescriptions.push({
      title: 'Sous-type',
      text: offerData.showSubTypeName,
    })
  }

  if (conditionalFields.includes('speaker')) {
    artisticInfoDescriptions.push({
      title: 'Intervenant',
      text: offerData.speaker,
    })
  }
  if (conditionalFields.includes('author')) {
    artisticInfoDescriptions.push({ title: 'Auteur', text: offerData.author })
  }
  if (conditionalFields.includes('visa')) {
    artisticInfoDescriptions.push({
      title: 'Visa d’exploitation',
      text: offerData.visa,
    })
  }
  if (conditionalFields.includes('ean')) {
    artisticInfoDescriptions.push({ title: 'EAN-13', text: offerData.ean })
  }
  if (conditionalFields.includes('stageDirector')) {
    artisticInfoDescriptions.push({
      title: 'Metteur en scène',
      text: offerData.stageDirector,
    })
  }
  if (conditionalFields.includes('performer')) {
    artisticInfoDescriptions.push({
      title: 'Interprète',
      text: offerData.performer,
    })
  }
  if (conditionalFields.includes('durationMinutes')) {
    artisticInfoDescriptions.push({
      title: 'Durée',
      text: offerData.durationMinutes
        ? `${offerData.durationMinutes} min`
        : '-',
    })
  }

  const practicalInfoDescriptions: Description[] = []
  if (offerData.withdrawalType) {
    practicalInfoDescriptions.push({
      title: 'Précisez la façon dont vous distribuerez les billets',
      text: OFFER_WITHDRAWAL_TYPE_LABELS[offerData.withdrawalType],
    })
  }
  practicalInfoDescriptions.push({
    title: 'Informations de retrait',
    text:
      /* istanbul ignore next: DEBT, TO FIX */
      offerData.withdrawalDetails || ' - ',
  })

  if (offerData.withdrawalDelay) {
    practicalInfoDescriptions.push({
      title: 'Heure de retrait',
      text: `${getDelayToFrenchText(offerData.withdrawalDelay)} avant le début de l’évènement`,
    })
  }
  if (offerData.bookingContact) {
    practicalInfoDescriptions.push({
      title: 'Email de contact',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.bookingContact || ' - ',
    })
  }

  const displayArtisticInformations = ARTISTIC_INFORMATION_FIELDS.some(
    (field) => conditionalFields.includes(field)
  )

  return (
    <>
      <SummarySection
        title="Description"
        editLink={getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })}
        aria-label="Modifier la description de l’offre"
        shouldShowDivider
      >
        <SummarySubSection
          title="À propos de votre offre"
          shouldShowDivider={false}
        >
          <SummaryDescriptionList descriptions={aboutDescriptions} />
        </SummarySubSection>
        <SummarySubSection title="Type d’offre" shouldShowDivider={false}>
          <SummaryDescriptionList descriptions={offerTypeDescriptions} />
        </SummarySubSection>
        {displayArtisticInformations && (
          <SummarySubSection
            title="Informations artistiques"
            shouldShowDivider={false}
          >
            <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
          </SummarySubSection>
        )}
      </SummarySection>
      <SummarySection
        title="Localisation"
        editLink={getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })}
        aria-label="Modifier la localisation de l’offre"
        shouldShowDivider
      >
        {!offer.isDigital && (
          <SummarySubSection
            title="Localisation de l’offre"
            shouldShowDivider={false}
          >
            <SummaryDescriptionList
              listDataTestId="localisation-offer-details"
              descriptions={[
                {
                  title: 'Intitulé',
                  text: offerData.location?.label ?? '-',
                },
                {
                  title: 'Adresse',
                  text: offerData.location
                    ? computeAddressDisplayName(offerData.location, false)
                    : '-',
                },
              ]}
            />
          </SummarySubSection>
        )}
        <SummarySubSection title="Retrait de l’offre" shouldShowDivider={false}>
          <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
        </SummarySubSection>
        <AccessibilitySummarySection
          accessibleItem={offer}
          accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
          shouldShowDivider={false}
        />
        <SummarySubSection
          title="Notifications des réservations"
          shouldShowDivider={false}
        >
          <SummaryDescriptionList
            descriptions={[
              {
                title: 'Email auquel envoyer les notifications',
                /* istanbul ignore next: DEBT, TO FIX */
                text: offerData.bookingEmail || ' - ',
              },
            ]}
          />
        </SummarySubSection>
      </SummarySection>
    </>
  )
}

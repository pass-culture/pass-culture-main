import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { getDelayToFrenchText } from 'commons/utils/date'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { Markdown } from 'components/Markdown/Markdown'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { serializeOfferSectionData } from 'pages/IndividualOfferSummary/commons/serializer'
import { useLocation } from 'react-router'
import { computeAddressDisplayName } from 'repository/venuesService'
import useSWR from 'swr'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './OfferSection.module.scss'

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
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const musicTypes = musicTypesQuery.data

  const offerData = serializeOfferSectionData(
    offer,
    categories,
    subCategories,
    musicTypes
  )

  if (musicTypesQuery.isLoading) {
    return <Spinner />
  }

  const offerTypeDescriptions: Description[] = [
    { title: 'Catégorie', text: offerData.categoryName },
    { title: 'Sous-catégorie', text: offerData.subCategoryName },
  ]

  const aboutDescriptions: Description[] = [
    {
      title: 'Structure',
      text: offerData.venuePublicName || offerData.venueName,
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

  const artisticInformationsFields = [
    'speaker',
    'author',
    'visa',
    'stageDirector',
    'performer',
    'ean',
    'durationMinutes',
  ]

  const displayArtisticInformations = artisticInformationsFields.some((field) =>
    conditionalFields.includes(field)
  )

  return (
    <SummarySection
      title="Détails de l’offre"
      editLink={getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
        mode:
          mode === OFFER_WIZARD_MODE.READ_ONLY
            ? OFFER_WIZARD_MODE.EDITION
            : mode,
        isOnboarding,
      })}
      aria-label="Modifier les détails de l’offre"
      className={styles['cancel-title-margin']}
    >
      <SummarySubSection title="À propos de votre offre">
        <SummaryDescriptionList descriptions={aboutDescriptions} />
      </SummarySubSection>
      <SummarySubSection title="Type d’offre">
        <SummaryDescriptionList descriptions={offerTypeDescriptions} />
      </SummarySubSection>
      {displayArtisticInformations && (
        <SummarySubSection title="Informations artistiques">
          <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
        </SummarySubSection>
      )}
      <SummarySection
        title="Informations pratiques"
        editLink={getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode:
            mode === OFFER_WIZARD_MODE.READ_ONLY
              ? OFFER_WIZARD_MODE.EDITION
              : mode,
          isOnboarding,
        })}
        aria-label="Modifier les informations pratiques de l’offre"
      >
        {!offer.isDigital && (
          <SummarySubSection title="Localisation de l’offre">
            <SummaryDescriptionList
              listDataTestId="localisation-offer-details"
              descriptions={[
                {
                  title: 'Intitulé',
                  text: offerData.address?.label ?? '-',
                },
                {
                  title: 'Adresse',
                  text: offerData.address
                    ? computeAddressDisplayName(offerData.address, false)
                    : '-',
                },
              ]}
            />
          </SummarySubSection>
        )}
        <SummarySubSection title="Retrait de l’offre">
          <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
        </SummarySubSection>
        <AccessibilitySummarySection
          accessibleItem={offer}
          accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
        />
        <SummarySubSection title="Notifications des réservations">
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
    </SummarySection>
  )
}

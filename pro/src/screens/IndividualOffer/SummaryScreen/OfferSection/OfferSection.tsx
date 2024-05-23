import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import useActiveFeature from 'hooks/useActiveFeature'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import Spinner from 'ui-kit/Spinner/Spinner'

import { serializeOfferSectionData } from './serializer'
import humanizeDelay from './utils'

interface OfferSummaryProps {
  offer: GetIndividualOfferResponseModel
  conditionalFields: string[]
}

const OfferSummary = ({
  conditionalFields,
  offer,
}: OfferSummaryProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const musicTypes = musicTypesQuery.data

  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )
  const isTiteliveMusicGenreEnabled = useActiveFeature(
    'ENABLE_PRO_TITELIVE_MUSIC_GENRES'
  )

  const offerData = serializeOfferSectionData(
    offer,
    categories,
    subCategories,
    isTiteliveMusicGenreEnabled,
    musicTypes
  )

  const editLink = getIndividualOfferUrl({
    offerId: offerData.id,
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
  })

  if (musicTypesQuery.isLoading) {
    return <Spinner />
  }

  const offerTypeDescriptions: Description[] = [
    { title: 'Catégorie', text: offerData.categoryName },
    { title: 'Sous-catégorie', text: offerData.subCategoryName },
  ]
  if (conditionalFields.includes('musicType')) {
    offerTypeDescriptions.push({
      title: 'Genre musical',
      text: offerData.musicTypeName || '-',
    })
  }
  if (offerData.musicSubTypeName && !isTiteliveMusicGenreEnabled) {
    offerTypeDescriptions.push({
      title: 'Sous-genre',
      text: offerData.musicSubTypeName,
    })
  }
  if (conditionalFields.includes('showType')) {
    offerTypeDescriptions.push({
      title: 'Type de spectacle',
      text: offerData.showTypeName || '-',
    })
  }
  if (offerData.showSubTypeName) {
    offerTypeDescriptions.push({
      title: 'Sous-type',
      text: offerData.showSubTypeName,
    })
  }

  const artisticInfoDescriptions: Description[] = [
    { title: 'Titre de l’offre', text: offerData.name },
    { title: 'Description', text: offerData.description || '-' },
  ]
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

  const practicalInfoDescriptions: Description[] = [
    { title: 'Structure', text: offerData.offererName },
    {
      title: 'Lieu',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.venuePublicName || offerData.venueName,
    },
    {
      title: 'Informations de retrait',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.withdrawalDetails || ' - ',
    },
  ]
  if (offerData.withdrawalType) {
    practicalInfoDescriptions.push({
      title: 'Précisez la façon dont vous distribuerez les billets',
      text: OFFER_WITHDRAWAL_TYPE_LABELS[offerData.withdrawalType],
    })
  }
  if (offerData.withdrawalDelay) {
    practicalInfoDescriptions.push({
      title: 'Heure de retrait',
      text: `${humanizeDelay(offerData.withdrawalDelay)} avant le début de l’évènement`,
    })
  }
  if (isBookingContactEnabled && offerData.bookingContact) {
    practicalInfoDescriptions.push({
      title: 'Email de contact',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.bookingContact || ' - ',
    })
  }
  if (conditionalFields.includes('url')) {
    practicalInfoDescriptions.push({
      title: 'URL d’accès à l’offre',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.url || ' - ',
    })
  }

  return (
    <SummarySection
      title="Détails de l’offre"
      editLink={editLink}
      aria-label="Modifier les détails de l’offre"
    >
      <SummarySubSection title="Type d’offre">
        <SummaryDescriptionList descriptions={offerTypeDescriptions} />
      </SummarySubSection>

      <SummarySubSection title="Informations artistiques">
        <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
      </SummarySubSection>

      <SummarySubSection title="Informations pratiques">
        <SummaryDescriptionList descriptions={practicalInfoDescriptions} />
      </SummarySubSection>

      <AccessibilitySummarySection
        accessibleItem={offer}
        accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
      />

      <SummarySubSection title="Lien pour le grand public">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'URL de votre site ou billetterie',
              /* istanbul ignore next: DEBT, TO FIX */
              text: offerData.externalTicketOfficeUrl || ' - ',
            },
          ]}
        />
      </SummarySubSection>

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
  )
}

export default OfferSummary

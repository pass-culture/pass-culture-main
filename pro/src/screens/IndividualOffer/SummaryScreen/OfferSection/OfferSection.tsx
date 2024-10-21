import cn from 'classnames'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { computeAddressDisplayName } from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './OfferSection.module.scss'
import { serializeOfferSectionData } from './serializer'
import { humanizeDelay } from './utils'

interface OfferSummaryProps {
  offer: GetIndividualOfferWithAddressResponseModel
  conditionalFields: string[]
  isEventPublicationFormShown: boolean
}

export const OfferSection = ({
  conditionalFields,
  offer,
  isEventPublicationFormShown,
}: OfferSummaryProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const musicTypes = musicTypesQuery.data

  const isSplitOfferEnabled = useActiveFeature('WIP_SPLIT_OFFER')

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

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
  if (!isSplitOfferEnabled) {
    if (conditionalFields.includes('musicType')) {
      offerTypeDescriptions.push({
        title: 'Genre musical',
        text: offerData.musicTypeName || '-',
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
  }
  const aboutDescriptions: Description[] = [
    { title: 'Titre de l’offre', text: offerData.name },
    { title: 'Description', text: offerData.description || '-' },
  ]
  const venueName = offerData.venuePublicName || offerData.venueName
  if (isOfferAddressEnabled) {
    aboutDescriptions.unshift({
      title: 'Qui propose l’offre',
      text: venueName,
    })
  } else if (isSplitOfferEnabled) {
    aboutDescriptions.unshift({
      title: 'Lieu',
      text: venueName,
    })
  } else {
    aboutDescriptions.push({
      title: 'Lieu',
      text: venueName,
    })
  }
  const artisticInfoDescriptions: Description[] = []
  if (!isSplitOfferEnabled) {
    artisticInfoDescriptions.push({
      title: 'Titre de l’offre',
      text: offerData.name,
    })
    artisticInfoDescriptions.push({
      title: 'Description',
      text: offerData.description || '-',
    })
  } else {
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
  if (!isSplitOfferEnabled) {
    practicalInfoDescriptions.push({
      title: 'Structure',
      text: offerData.offererName,
    })
    practicalInfoDescriptions.push({
      title: 'Lieu',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.venuePublicName || offerData.venueName,
    })
  }
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
      text: `${humanizeDelay(offerData.withdrawalDelay)} avant le début de l’évènement`,
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
  if (conditionalFields.includes('url')) {
    practicalInfoDescriptions.push({
      title: 'URL d’accès à l’offre',
      text:
        /* istanbul ignore next: DEBT, TO FIX */
        offerData.url || ' - ',
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
        step: isSplitOfferEnabled
          ? OFFER_WIZARD_STEP_IDS.DETAILS
          : OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode:
          mode === OFFER_WIZARD_MODE.READ_ONLY
            ? OFFER_WIZARD_MODE.EDITION
            : mode,
      })}
      aria-label="Modifier les détails de l’offre"
      className={cn({
        [styles['cancel-title-margin']]: isEventPublicationFormShown,
      })}
    >
      {isSplitOfferEnabled ? (
        <>
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
        </>
      ) : (
        <>
          <SummarySubSection title="Type d’offre">
            <SummaryDescriptionList descriptions={offerTypeDescriptions} />
          </SummarySubSection>

          <SummarySubSection title="Informations artistiques">
            <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
          </SummarySubSection>
        </>
      )}

      {isSplitOfferEnabled ? (
        <SummarySection
          title="Informations pratiques"
          editLink={getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
            mode:
              mode === OFFER_WIZARD_MODE.READ_ONLY
                ? OFFER_WIZARD_MODE.EDITION
                : mode,
          })}
          aria-label="Modifier les informations pratiques de l’offre"
        >
          {!offerData.isVenueVirtual && isOfferAddressEnabled && (
            <SummarySubSection title="Localisation de l’offre">
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'Adresse',
                    text: computeAddressDisplayName(offerData.address!),
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
      ) : (
        <>
          <SummarySubSection title="Informations pratiques">
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
        </>
      )}
    </SummarySection>
  )
}

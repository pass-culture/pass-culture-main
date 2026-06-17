import { useLocation } from 'react-router'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1/new'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CULTURAL_OUTREACH_ALLOWED_ACTIVITIES,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { computeAddressDisplayName } from '@/commons/format/venuesService'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { getDelayToFrenchText } from '@/commons/utils/date'
import { AccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { Markdown } from '@/components/Markdown/Markdown'
import { ARTISTIC_INFORMATION_FIELDS } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/DetailsSubForm/DetailsSubForm'
import { serializeOfferSectionData } from '@/pages/IndividualOfferSummary/commons/serializer'
import {
  type Description,
  SummaryDescriptionList,
} from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

const EMPTY_TEXT = '-'

function buildPracticalInfoDescriptions(
  offerData: ReturnType<typeof serializeOfferSectionData>
): Description[] {
  return [
    offerData.withdrawalType && {
      title: 'Précisez la façon dont vous distribuerez les billets',
      text: OFFER_WITHDRAWAL_TYPE_LABELS[offerData.withdrawalType],
    },
    {
      title: 'Informations de retrait',
      text: offerData.withdrawalDetails || EMPTY_TEXT,
    },
    offerData.withdrawalDelay && {
      title: 'Heure de retrait',
      text: `${getDelayToFrenchText(offerData.withdrawalDelay)} avant le début de l'évènement`,
    },
    offerData.bookingContact && {
      title: 'Email de contact',
      text: offerData.bookingContact || EMPTY_TEXT,
    },
  ].filter(Boolean) as Description[]
}

function buildArtisticInfoDescriptions(
  conditionalFields: string[],
  offerData: ReturnType<typeof serializeOfferSectionData>
): Description[] {
  const hasField = (field: string) => conditionalFields.includes(field)

  return [
    hasField('musicType') && {
      title: 'Genre musical',
      text: offerData.musicTypeName || EMPTY_TEXT,
    },
    hasField('showType') && {
      title: 'Type de spectacle',
      text: offerData.showTypeName || EMPTY_TEXT,
    },
    offerData.showSubTypeName && {
      title: 'Sous-type',
      text: offerData.showSubTypeName,
    },
    hasField('speaker') && { title: 'Intervenant', text: offerData.speaker },
    hasField('author') && { title: 'Auteur', text: offerData.author },
    hasField('visa') && { title: 'Visa d’exploitation', text: offerData.visa },
    hasField('ean') && { title: 'EAN-13', text: offerData.ean },
    hasField('stageDirector') && {
      title: 'Metteur en scène',
      text: offerData.stageDirector,
    },
    hasField('performer') && { title: 'Interprète', text: offerData.performer },
    hasField('durationMinutes') && {
      title: 'Durée',
      text: offerData.durationMinutes
        ? `${offerData.durationMinutes} min`
        : EMPTY_TEXT,
    },
  ].filter(Boolean) as Description[]
}

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

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isCulturalOutreachEnabled = useActiveFeature(
    'WIP_ENABLE_CULTURAL_OUTREACH'
  )

  const canClaimCulturalOutreach =
    isCulturalOutreachEnabled &&
    selectedPartnerVenue.activity !== null &&
    CULTURAL_OUTREACH_ALLOWED_ACTIVITIES.has(selectedPartnerVenue.activity)

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
    ...(canClaimCulturalOutreach
      ? [
          {
            title: 'Inclut une action de médiation spécifique',
            text: offer.hasCulturalOutreachClaim ? 'Oui' : 'Non',
          },
        ]
      : []),
    {
      title: 'Description',
      text: !offerData.description ? (
        EMPTY_TEXT
      ) : (
        <Markdown markdownText={offerData.description} />
      ),
    },
  ].concat(
    offer.isDigital
      ? {
          title: 'URL d’accès à l’offre',
          text: offer.url || EMPTY_TEXT,
        }
      : []
  )

  const artisticInfoDescriptions = buildArtisticInfoDescriptions(
    conditionalFields,
    offerData
  )

  const practicalInfoDescriptions = buildPracticalInfoDescriptions(offerData)

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
                  text: offerData.location?.label ?? EMPTY_TEXT,
                },
                {
                  title: 'Adresse',
                  text: offerData.location
                    ? // TODO (amine) to remove once model migrated to Pydantic V2
                      // @ts-expect-error
                      computeAddressDisplayName(offerData.location, false)
                    : EMPTY_TEXT,
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
                text: offerData.bookingEmail || EMPTY_TEXT,
              },
            ]}
          />
        </SummarySubSection>
      </SummarySection>
    </>
  )
}

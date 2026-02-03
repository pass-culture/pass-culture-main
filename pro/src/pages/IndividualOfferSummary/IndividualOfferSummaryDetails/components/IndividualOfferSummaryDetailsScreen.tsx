import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { AccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { Markdown } from '@/components/Markdown/Markdown'
import { OfferAppPreview } from '@/components/OfferAppPreview/OfferAppPreview'
import { SummaryAside } from '@/components/SummaryLayout/SummaryAside'
import { SummaryContent } from '@/components/SummaryLayout/SummaryContent'
import {
  type Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from '@/components/SummaryLayout/SummaryLayout'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import { Banner } from '@/design-system/Banner/Banner'
import { ButtonVariant } from '@/design-system/Button/types'
import phoneStrokeIcon from '@/icons/stroke-phone.svg'
import { ARTISTIC_INFORMATION_FIELDS } from '@/pages/IndividualOffer/IndividualOfferDetails/components/DetailsForm/DetailsSubForm/DetailsSubForm'
import { serializeOfferSectionData } from '@/pages/IndividualOfferSummary/commons/serializer'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferSummaryDetailsScreen.module.scss'

export interface IndividualOfferSummaryDetailsScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryDetailsScreen({
  offer,
}: Readonly<IndividualOfferSummaryDetailsScreenProps>) {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()

  const { musicTypes } = useMusicTypes()
  const offerData = serializeOfferSectionData(
    offer,
    categories,
    subCategories,
    musicTypes
  )

  const subcategory = subCategories.find(
    (sucategory) => sucategory.id === offer.subcategoryId
  )
  const conditionalFields = subcategory?.conditionalFields || []

  const aboutDescriptions: Description[] = [
    {
      title: 'Structure',
      text: offerData.venuePublicName,
    },
    { title: 'Titre de l’offre', text: offerData.name },
    {
      title: 'Description',
      text: !offerData.description ? (
        ''
      ) : (
        <Markdown markdownText={offerData.description} />
      ),
    },
  ]

  const typeDescriptions: Description[] = [
    { title: 'Catégorie', text: offerData.categoryName },
    { title: 'Sous-catégorie', text: offerData.subCategoryName },
  ]

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
  if (subcategory?.isEvent) {
    artisticInfoDescriptions.push({
      title: 'Durée',
      text: offerData.durationMinutes
        ? `${offerData.durationMinutes} min`
        : '-',
    })
  }

  const displayArtisticInformations = ARTISTIC_INFORMATION_FIELDS.some(
    (field) => conditionalFields.includes(field) || subcategory?.isEvent
  )

  const cannotEditDetails = offerData.isProductBased

  return (
    <SummaryLayout>
      <SummaryContent>
        {cannotEditDetails && (
          <Banner
            title="Informations verrouillées"
            description="Ces informations proviennent de l'EAN et ne peuvent pas être modifiées."
          />
        )}

        <SummarySection
          title="Description"
          {...(cannotEditDetails
            ? {}
            : {
                editLink: getIndividualOfferUrl({
                  offerId: offer.id,
                  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
                'aria-label': 'Modifier la description de l’offre',
              })}
        >
          <SummarySubSection title="A propos de votre offre">
            <SummaryDescriptionList descriptions={aboutDescriptions} />
          </SummarySubSection>
          <SummarySubSection title="Type d’offre">
            <SummaryDescriptionList descriptions={typeDescriptions} />
          </SummarySubSection>
          {displayArtisticInformations && (
            <SummarySubSection title="Informations artistiques">
              <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
            </SummarySubSection>
          )}
          <AccessibilitySummarySection
            accessibleItem={offer}
            accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
            shouldShowDivider
          />
        </SummarySection>
      </SummaryContent>

      <SummaryAside>
        <div className={styles['title-container']}>
          <SvgIcon
            src={phoneStrokeIcon}
            alt=""
            width="24"
            className={styles['icon-info-phone']}
          />
          <h2 className={styles['title']}>Aperçu dans l’app</h2>
        </div>

        <OfferAppPreview offer={offer} />

        {mode === OFFER_WIZARD_MODE.READ_ONLY && (
          <DisplayOfferInAppLink
            id={offer.id}
            variant={ButtonVariant.SECONDARY}
            label="Visualiser dans l’app"
            fullWidth
          />
        )}
      </SummaryAside>
    </SummaryLayout>
  )
}

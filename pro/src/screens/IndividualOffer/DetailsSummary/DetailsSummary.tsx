import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OfferAppPreview } from 'components/OfferAppPreview/OfferAppPreview'
import { SummaryAside } from 'components/SummaryLayout/SummaryAside'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { DisplayOfferInAppLink } from '../SummaryScreen/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { serializeOfferSectionData } from '../SummaryScreen/OfferSection/serializer'

import styles from './DetailsSummary.module.scss'

type DetailsSummaryScreenProps = {
  offer: GetIndividualOfferResponseModel
}

export function DetailsSummaryScreen({ offer }: DetailsSummaryScreenProps) {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const offerData = serializeOfferSectionData(
    offer,
    categories,
    subCategories,
    musicTypesQuery.data
  )

  const subcategory = subCategories.find(
    (sucategory) => sucategory.id === offer.subcategoryId
  )
  const conditionalFields = subcategory?.conditionalFields || []

  const aboutDescriptions: Description[] = [
    { title: 'Title de l’offre', text: offerData.name },
    { title: 'Description', text: offerData.description },
    { title: 'Lieu', text: offerData.venuePublicName ?? offerData.venueName },
  ]

  const typeDescriptions: Description[] = [
    { title: 'Catégorie', text: offerData.categoryName },
    { title: 'Sous-catégorie', text: offerData.subCategoryName },
  ]
  if (conditionalFields.includes('musicType')) {
    typeDescriptions.push({
      title: 'Genre musical',
      text: offerData.musicTypeName || '-',
    })
  }
  if (conditionalFields.includes('showType')) {
    typeDescriptions.push({
      title: 'Type de spectacle',
      text: offerData.showTypeName || '-',
    })
  }
  if (offerData.showSubTypeName) {
    typeDescriptions.push({
      title: 'Sous-type',
      text: offerData.showSubTypeName,
    })
  }

  const artisticInfoDescriptions: Description[] = []
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

  return (
    <SummaryLayout>
      <SummaryContent>
        <SummarySection
          title="Détails de l’offre"
          editLink={getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.DETAILS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          aria-label="Modifier les détails de l’offre"
        >
          <SummarySubSection title="A propos de votre offre">
            <SummaryDescriptionList descriptions={aboutDescriptions} />
          </SummarySubSection>
          <SummarySubSection title="Type d’offre">
            <SummaryDescriptionList descriptions={typeDescriptions} />
          </SummarySubSection>
          <SummarySubSection title="Informations artistiques">
            <SummaryDescriptionList descriptions={artisticInfoDescriptions} />
          </SummarySubSection>
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
          <div>
            <DisplayOfferInAppLink
              id={offer.id}
              variant={ButtonVariant.SECONDARY}
              className={styles['app-link']}
            >
              Visualiser dans l’app
            </DisplayOfferInAppLink>
          </div>
        )}
      </SummaryAside>
    </SummaryLayout>
  )
}

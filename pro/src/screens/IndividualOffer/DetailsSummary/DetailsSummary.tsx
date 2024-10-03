import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
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
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { DisplayOfferInAppLink } from '../SummaryScreen/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { serializeOfferSectionData } from '../SummaryScreen/OfferSection/serializer'

import styles from './DetailsSummary.module.scss'

type DetailsSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function DetailsSummaryScreen({ offer }: DetailsSummaryScreenProps) {
  const mode = useOfferWizardMode()
  const { categories, subCategories } = useIndividualOfferContext()
  const isSplitOfferEnabled = useActiveFeature('WIP_SPLIT_OFFER')
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

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
    { title: 'Titre de l’offre', text: offerData.name },
    { title: 'Description', text: offerData.description },
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

  const artisticInformationsFields = [
    'speaker',
    'author',
    'visa',
    'stageDirector',
    'performer',
    'ean',
    'durationMinutes',
    'showType',
    'gtl_id',
  ]

  const displayArtisticInformations = artisticInformationsFields.some(
    (field) => conditionalFields.includes(field) || subcategory?.isEvent
  )

  const cannotEditDetails = offerData.isProductBased

  return (
    <SummaryLayout>
      <SummaryContent>
        {cannotEditDetails && (
          <Callout variant={CalloutVariant.DEFAULT}>
            Les informations de cette page ne sont pas modifiables car elles
            sont liées à l’EAN renseigné.
          </Callout>
        )}
        <SummarySection
          title="Détails de l’offre"
          {...(cannotEditDetails
            ? {}
            : {
                editLink: getIndividualOfferUrl({
                  offerId: offer.id,
                  step: OFFER_WIZARD_STEP_IDS.DETAILS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
                'aria-label': 'Modifier les détails de l’offre',
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

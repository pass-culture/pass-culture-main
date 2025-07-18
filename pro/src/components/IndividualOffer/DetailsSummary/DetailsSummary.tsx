import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Markdown } from 'components/Markdown/Markdown'
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
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { DisplayOfferInAppLink } from '../../../pages/IndividualOffer/IndividualOfferSummary/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { serializeOfferSectionData } from '../../../pages/IndividualOffer/IndividualOfferSummary/components/OfferSection/serializer'

import styles from './DetailsSummary.module.scss'

type DetailsSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
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
    {
      title: 'Structure',
      text: offerData.venuePublicName || offerData.venueName,
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
  ].concat(
    offer.isDigital
      ? {
          title: 'URL d’accès à l’offre',
          text: offer.url || ' - ',
        }
      : []
  )

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
          <Callout>
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

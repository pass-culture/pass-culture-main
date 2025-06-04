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

import { DisplayOfferInAppLink } from '../SummaryScreen/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { serializeOfferSectionData } from '../SummaryScreen/OfferSection/serializer'

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

import {
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import OfferEducationalActions from 'components/OfferEducationalActions'
import { isCollectiveOfferTemplate, Mode } from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  reloadCollectiveOffer: () => void
  mode: Mode
}

export const CollectiveOfferSummaryEditionScreen = ({
  offer,
  reloadCollectiveOffer,
  mode,
}: CollectiveOfferSummaryEditionProps) => {
  const offerEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/edition`

  const stockEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/stocks/edition`

  const visibilityEditLink = `/offre/${offer.id}/collectif/visibilite/edition`

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        isBooked={
          isCollectiveOfferTemplate(offer)
            ? false
            : Boolean(offer.collectiveStock?.isBooked)
        }
        offer={offer}
        reloadCollectiveOffer={reloadCollectiveOffer}
        mode={mode}
      />

      <CollectiveOfferSummary
        offer={offer}
        offerEditLink={offerEditLink}
        stockEditLink={stockEditLink}
        visibilityEditLink={visibilityEditLink}
      />

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{ isExternal: false, to: computeCollectiveOffersUrl({}) }}
          >
            Retour à la liste des offres
          </ButtonLink>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}

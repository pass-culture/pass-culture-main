import {
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { CollectiveOfferSummary } from 'components/CollectiveOfferSummary/CollectiveOfferSummary'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import { Mode, isCollectiveOfferTemplate } from 'core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  mode: Mode
}

export const CollectiveOfferSummaryEditionScreen = ({
  offer,
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
            to={computeCollectiveOffersUrl({})}
          >
            Retour à la liste des offres
          </ButtonLink>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}

import {
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { isCollectiveOffer, Mode } from 'commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import { withCollectiveOfferFromParams } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferSummary } from 'pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/CollectiveOfferSummary'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { BookableOfferSummary } from '../BookableOfferSummary/BookableOfferSummary'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export const CollectiveOfferSummaryEdition = ({
  offer,
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

  const isNewCollectiveOfferDetailPageActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE'
  )

  if (isNewCollectiveOfferDetailPageActive && isCollectiveOffer(offer)) {
    return <BookableOfferSummary offer={offer} />
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={offer.isTemplate}
      offer={offer}
    >
      <OfferEducationalActions
        className={styles.actions}
        offer={offer}
        mode={Mode.EDITION}
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
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryEdition
)

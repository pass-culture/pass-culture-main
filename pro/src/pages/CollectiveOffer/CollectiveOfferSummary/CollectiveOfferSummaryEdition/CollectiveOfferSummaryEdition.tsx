import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { isCollectiveOffer, Mode } from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { Button } from '@/design-system/Button/Button'
import { withCollectiveOfferFromParams } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferSummary } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/CollectiveOfferSummary'

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

  if (isCollectiveOffer(offer)) {
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
          <Button
            as="a"
            to={computeCollectiveOffersUrl({}, undefined, offer.isTemplate)}
            label="Retour à la liste des offres"
          />
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

import { CollectiveOfferTemplateAllowedAction } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { ShareLinkDrawer } from '@/components/CollectiveOffer/ShareLinkDrawer/ShareLinkDrawer'
import { Button } from '@/design-system/Button/Button'
import { AdagePreviewLayout } from '@/pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { PreviewHeader } from '../components/PreviewHeader'
import styles from './CollectiveOfferPreviewEdition.module.scss'

export const CollectiveOfferPreviewEdition = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/T-${offer.id}/collectif/recapitulatif`
    : `/offre/${offer.id}/collectif/recapitulatif`

  const canShareOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_SHARE
  )

  return (
    <BasicLayout mainHeading="Aperçu de l’offre" isStickyActionBarInChild>
      {isCollectiveOfferTemplate(offer) && canShareOffer && (
        <div className={styles['share-link-drawer']}>
          <ShareLinkDrawer offerId={offer.id} />
        </div>
      )}
      <PreviewHeader offer={offer} />
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button as="a" to={backRedirectionUrl} label="Retour vers l’offre" />
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewEdition
)

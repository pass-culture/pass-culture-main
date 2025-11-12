import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { ShareLinkDrawer } from '@/components/CollectiveOffer/ShareLinkDrawer/ShareLinkDrawer'
import { AdagePreviewLayout } from '@/pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { PreviewHeader } from '../components/PreviewHeader'
import styles from './CollectiveOfferPreviewEdition.module.scss'

export const CollectiveOfferPreviewEdition = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const isCollectiveOfferTemplateShareLinkEnabled = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_OFFER_TEMPLATE_SHARE_LINK'
  )

  const backRedirectionUrl = offer.isTemplate
    ? `/offre/T-${offer.id}/collectif/recapitulatif`
    : `/offre/${offer.id}/collectif/recapitulatif`

  return (
    <BasicLayout mainHeading="Aperçu de l’offre" isStickyActionBarInChild>
      {isCollectiveOfferTemplate(offer) &&
        isCollectiveOfferTemplateShareLinkEnabled && (
          <div className={styles['share-link-drawer']}>
            <ShareLinkDrawer offerId={offer.id} />
          </div>
        )}
      <PreviewHeader offer={offer} />
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink variant={ButtonVariant.PRIMARY} to={backRedirectionUrl}>
            Retour vers l’offre
          </ButtonLink>
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

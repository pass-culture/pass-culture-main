import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import { AdagePreviewLayout } from '@/pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { Title } from '@/ui-kit/Title/Title'

import { PreviewHeader } from '../components/PreviewHeader'

export const CollectiveOfferPreviewEdition = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/T-${offer.id}/collectif/recapitulatif`
    : `/offre/${offer.id}/collectif/recapitulatif`

  return (
    <BasicLayout isStickyActionBarInChild>
      <Title level="1" title="Aperçu de l’offre" marginBottom="xxl" />
      <PreviewHeader offer={offer} />
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button
            as="router-link"
            to={backRedirectionUrl}
            label="Retour vers l’offre"
          />
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

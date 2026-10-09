import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
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

  return (
    <ContentLayout>
      <h1 className={styles['title']}>Aperçu de l’offre</h1>
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
    </ContentLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewEdition
)

import { Layout } from 'app/App/layout/Layout'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { AdagePreviewLayout } from 'pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferPreviewEdition.module.scss'

export const CollectiveOfferPreviewEdition = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/T-${offer.id}/collectif/recapitulatif`
    : `/offre/${offer.id}/collectif/recapitulatif`

  return (
    <Layout layout={'sticky-actions'} mainHeading='Aperçu de l’offre'>
      <p className={styles['preview-info']}>
        Voici à quoi ressemble votre offre une fois publiée sur la plateforme
        ADAGE.
      </p>
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink variant={ButtonVariant.PRIMARY} to={backRedirectionUrl}>
            Retour vers l’offre
          </ButtonLink>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewEdition
)

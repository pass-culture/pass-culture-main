import { AppLayout } from 'app/AppLayout'
import ActionsBarSticky from 'components/ActionsBarSticky'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import AdagePreviewLayout from 'pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferPreviewEdition.module.scss'

export const CollectiveOfferPreviewEdition = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/T-${offer.id}/collectif/recapitulatif`
    : `/offre/${offer.id}/collectif/recapitulatif`

  return (
    <AppLayout layout={'sticky-actions'}>
      <div>
        <h1>Aperçu de l’offre</h1>
        <p className={styles['preview-info']}>
          Voici à quoi ressemble votre offre une fois publiée sur ADAGE.
        </p>
        <AdagePreviewLayout offer={offer} />
        <ActionsBarSticky>
          <ActionsBarSticky.Left>
            <ButtonLink
              variant={ButtonVariant.PRIMARY}
              link={{
                to: backRedirectionUrl,
                isExternal: false,
              }}
            >
              Retour vers l’offre
            </ButtonLink>
          </ActionsBarSticky.Left>
        </ActionsBarSticky>
      </div>
      <RouteLeavingGuardCollectiveOfferCreation />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewEdition
)

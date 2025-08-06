import { useParams } from 'react-router'

import { Mode } from '@/commons/core/OfferEducational/types'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { CollectiveOfferSummary } from '../components/CollectiveOfferSummary/CollectiveOfferSummary'
import styles from './CollectiveOfferSummaryCreation.module.scss'

export const CollectiveOfferSummaryCreation = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const { requete: requestId } = useParams()

  const nextRedirectionUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/creation/apercu`
    : `/offre/${offer.id}/collectif/creation/apercu`

  const backRedirectionUrl = offer.isTemplate
    ? `/offre/collectif/vitrine/${offer.id}/creation`
    : `/offre/${offer.id}/collectif/visibilite${
        requestId ? `?requete=${requestId}` : ''
      }`

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={isTemplate}
      isCreation={true}
      offer={offer}
    >
      <div className={styles['summary']}>
        <CollectiveOfferSummary
          offer={offer}
          offerEditLink={`/offre/collectif${
            offer.isTemplate ? '/vitrine' : ''
          }/${offer.id}/creation`}
          stockEditLink={`/offre/${offer.id}/collectif/stocks`}
          visibilityEditLink={`/offre/${offer.id}/collectif/visibilite`}
        />
        <ActionsBarSticky>
          <ActionsBarSticky.Left>
            <ButtonLink
              variant={ButtonVariant.SECONDARY}
              to={backRedirectionUrl}
            >
              Retour
            </ButtonLink>
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right dirtyForm={false} mode={Mode.CREATION}>
            <ButtonLink variant={ButtonVariant.PRIMARY} to={nextRedirectionUrl}>
              Enregistrer et continuer
            </ButtonLink>
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </div>
      <RouteLeavingGuardCollectiveOfferCreation when={false} />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryCreation
)

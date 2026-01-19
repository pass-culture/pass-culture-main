import { useParams } from 'react-router'

import { Mode } from '@/commons/core/OfferEducational/types'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

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
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              to={backRedirectionUrl}
              label="Retour"
            />
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right dirtyForm={false} mode={Mode.CREATION}>
            <Button
              as="a"
              to={nextRedirectionUrl}
              label="Enregistrer et continuer"
            />
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

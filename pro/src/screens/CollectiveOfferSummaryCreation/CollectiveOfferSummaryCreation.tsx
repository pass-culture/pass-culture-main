import { useParams } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryCreation.module.scss'

interface CollectiveOfferSummaryCreationProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

const CollectiveOfferSummaryCreation = ({
  offer,
}: CollectiveOfferSummaryCreationProps) => {
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
            link={{
              to: backRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape précédente
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{
              to: nextRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape suivante
          </ButtonLink>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </div>
  )
}

export default CollectiveOfferSummaryCreation

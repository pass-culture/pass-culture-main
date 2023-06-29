import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import { Banner, Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import publishCollectiveOfferAdapter from './adapters/publishCollectiveOfferAdapter'
import publishCollectiveOfferTemplateAdapter from './adapters/publishCollectiveOfferTemplateAdapter'
import styles from './CollectiveOfferSummaryCreation.module.scss'

interface CollectiveOfferSummaryCreationProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
}

const CollectiveOfferSummaryCreation = ({
  offer,
  categories,
  setOffer,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()
  const navigate = useNavigate()

  const { requete: requestId } = useParams()

  const publishOffer = async () => {
    const confirmationUrl = offer.isTemplate
      ? `/offre/${offer.nonHumanizedId}/collectif/vitrine/confirmation`
      : `/offre/${computeURLCollectiveOfferId(
          offer.nonHumanizedId,
          offer.isTemplate
        )}/collectif/confirmation`

    if (offer.isTemplate) {
      const response = await publishCollectiveOfferTemplateAdapter(
        offer.nonHumanizedId
      )
      if (!response.isOk) {
        return notify.error(response.message)
      }
      setOffer(response.payload)
      return navigate(confirmationUrl)
    }

    const response = await publishCollectiveOfferAdapter(offer.nonHumanizedId)
    if (!response.isOk) {
      return notify.error(response.message)
    }
    setOffer(response.payload)
    return navigate(confirmationUrl)
  }
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/collectif/vitrine/${offer.nonHumanizedId}/creation`
    : `/offre/${offer.nonHumanizedId}/collectif/visibilite${
        requestId ? `?requete=${requestId}` : ''
      }`

  return (
    <div className={styles['summary']}>
      <Banner type="notification-info" className={styles['summary-banner']}>
        Vous y êtes presque !<br />
        Vérifiez les informations ci-dessous avant de publier votre offre.
      </Banner>
      <CollectiveOfferSummary
        offer={offer}
        categories={categories}
        offerEditLink={`/offre/collectif${offer.isTemplate ? '/vitrine' : ''}/${
          offer.nonHumanizedId
        }/creation`}
        stockEditLink={`/offre/${offer.nonHumanizedId}/collectif/stocks`}
        visibilityEditLink={`/offre/${offer.nonHumanizedId}/collectif/visibilite`}
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
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={publishOffer}>Publier l’offre</Button>{' '}
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </div>
  )
}

export default CollectiveOfferSummaryCreation

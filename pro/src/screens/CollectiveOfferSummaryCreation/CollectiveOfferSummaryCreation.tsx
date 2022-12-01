import React from 'react'
import { useHistory } from 'react-router-dom'

import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import FormLayout from 'components/FormLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useActiveFeature from 'hooks/useActiveFeature'
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
  const history = useHistory()

  const publishOffer = async () => {
    const confirmationUrl = offer.isTemplate
      ? `/offre/${offer.id}/collectif/vitrine/confirmation`
      : `/offre/${computeURLCollectiveOfferId(
          offer.id,
          offer.isTemplate
        )}/collectif/confirmation`

    if (offer.isTemplate) {
      const response = await publishCollectiveOfferTemplateAdapter(offer.id)
      if (!response.isOk) {
        return notify.error(response.message)
      }
      setOffer(response.payload)
      return history.push(confirmationUrl)
    }

    const response = await publishCollectiveOfferAdapter(offer.id)
    if (!response.isOk) {
      return notify.error(response.message)
    }
    setOffer(response.payload)
    return history.push(confirmationUrl)
  }
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/collectif/vitrine/${offer.id}/creation`
    : `/offre/${offer.id}/collectif/visibilite`

  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  return (
    <div className={styles['summary']}>
      <Banner type="notification-info" className={styles['summary-banner']}>
        Vous y êtes presque !<br />
        Vérifiez les informations ci-dessous avant de publier votre offre.
      </Banner>
      <CollectiveOfferSummary offer={offer} categories={categories} />
      {isOfferFormV3 ? (
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
      ) : (
        <FormLayout.Actions>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: backRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape précédente
          </ButtonLink>
          <Button onClick={publishOffer}>Publier l’offre</Button>
        </FormLayout.Actions>
      )}
    </div>
  )
}

export default CollectiveOfferSummaryCreation

import React from 'react'
import { Link, useHistory } from 'react-router-dom'

import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeOffersUrl } from 'core/Offers'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummary from 'new_components/CollectiveOfferSummary'
import FormLayout from 'new_components/FormLayout'
import { Banner, Button } from 'ui-kit'

import publishCollectiveOfferAdapter from './adapters/publishCollectiveOfferAdapter'
import publishCollectiveOfferTemplateAdapter from './adapters/publishCollectiveOfferTemplateAdapter'
import styles from './CollectiveOfferSummaryCreation.module.scss'

interface CollectiveOfferSummaryCreationProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
}

const CollectiveOfferSummaryCreation = ({
  offer,
  categories,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()
  const history = useHistory()

  const publishOffer = async () => {
    const confirmationUrl = `/offre/${computeURLCollectiveOfferId(
      offer.id,
      offer.isTemplate
    )}/collectif/confirmation`

    if (offer.isTemplate) {
      const response = await publishCollectiveOfferTemplateAdapter(offer.id)
      if (!response.isOk) {
        return notify.error(response.message)
      }
      return history.push(confirmationUrl)
    }

    const response = await publishCollectiveOfferAdapter(offer.id)
    if (!response.isOk) {
      return notify.error(response.message)
    }
    return history.push(confirmationUrl)
  }

  return (
    <div className={styles['summary']}>
      <Banner type="notification-info" className={styles['summary-banner']}>
        Vous y êtes presque !<br />
        Vérifiez les informations ci-dessous avant de publier votre offre.
      </Banner>
      <CollectiveOfferSummary offer={offer} categories={categories} />
      <FormLayout.Actions>
        <Link className="secondary-link" to={computeOffersUrl({})}>
          Annuler et quitter
        </Link>
        <Button onClick={publishOffer}>Publier l’offre</Button>
      </FormLayout.Actions>
    </div>
  )
}

export default CollectiveOfferSummaryCreation

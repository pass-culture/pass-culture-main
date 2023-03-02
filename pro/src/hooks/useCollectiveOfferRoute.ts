import { useEffect, useState } from 'react'
import { matchPath } from 'react-router'

import getCollectiveOfferAdapter, {
  GetCollectiveOfferAdapter,
} from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter, {
  GetCollectiveOfferTemplateAdapter,
} from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'

const useCollectiveOfferRoute = (
  pathname: string,
  offerIdFromParam?: string
) => {
  const [loadCollectiveOffer, setLoadCollectiveOffer] = useState<
    GetCollectiveOfferTemplateAdapter | GetCollectiveOfferAdapter
  >()
  const [offerId, setOfferId] = useState<string>()
  const [isCreation, setIsCreation] = useState<boolean>(false)
  const [isTemplate, setIsTemplate] = useState<boolean>(false)
  useEffect(() => {
    setIsCreation(
      [
        '/offre/:offerId/collectif/edition',
        '/offre/:offerId/collectif/recapitulatif',
        '/offre/:offerId/collectif/stocks/edition',
        '/offre/:offerId/collectif/visibilite/edition',
      ].find(route => matchPath(pathname, route)) === undefined
    )
    const splitOfferId = offerIdFromParam?.split('T-')

    const isTemplate =
      splitOfferId && splitOfferId.length === 1
        ? pathname.includes('vitrine') // creation
        : true // edition

    setOfferId(
      splitOfferId && splitOfferId.length > 1
        ? splitOfferId[1]
        : offerIdFromParam
    )
    setIsTemplate(isTemplate)
    setLoadCollectiveOffer(
      isTemplate ? getCollectiveOfferTemplateAdapter : getCollectiveOfferAdapter
    )
  }, [])

  return {
    offerId,
    isCreation,
    isTemplate,
    loadCollectiveOffer,
  }
}

export default useCollectiveOfferRoute

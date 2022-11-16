import { useHistory } from 'react-router'

import useNotification from 'hooks/useNotification'

import getCollectiveOfferFormDataApdater from '../adapters/getCollectiveOfferFormDataAdapter'
import getCollectiveOfferTemplateAdapter from '../adapters/getCollectiveOfferTemplateAdapter'
import postCollectiveOfferAdapter from '../adapters/postCollectiveOfferAdapter'

// TODO (atrancart): delete when feature flag is removed
export const oldCreateOfferFromTemplate = async (
  history: ReturnType<typeof useHistory>,
  templateOfferId: string
) => {
  history.push(`/offre/duplication/collectif/${templateOfferId}`)
}

export const createOfferFromTemplate = async (
  history: ReturnType<typeof useHistory>,
  notify: ReturnType<typeof useNotification>,
  templateOfferId: string
) => {
  const offerTemplateResponse = await getCollectiveOfferTemplateAdapter(
    templateOfferId
  )

  if (!offerTemplateResponse.isOk) {
    return notify.error(offerTemplateResponse.message)
  }

  const result = await getCollectiveOfferFormDataApdater({
    offererId: offerTemplateResponse.payload.venue.managingOffererId,
    offer: offerTemplateResponse.payload,
  })

  if (!result.isOk) {
    notify.error(result.message)
  }

  const { initialValues } = result.payload

  const { isOk, message, payload } = await postCollectiveOfferAdapter({
    offer: initialValues,
    offerTemplateId: templateOfferId,
  })

  if (!isOk) {
    return notify.error(message)
  }

  history.push(`/offre/collectif/${payload.id}/creation`)
}

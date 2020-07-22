import { requestData } from 'redux-thunk-data'

import { offerNormalizer } from '../../../../utils/normalizers'

export const getOffer = offerId =>
  requestData({
    apiPath: `/offers/${offerId}`,
    method: 'GET',
    normalizer: offerNormalizer,
  })

import get from 'lodash.get';

export default function getOffer (userMediation, offerId) {
  return get(userMediation, 'userMediationOffers', [])
    .find(o => offerId ? (o.id === offerId) : true)
}

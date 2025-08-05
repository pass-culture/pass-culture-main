import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'commons/core/Offers/constants'

import {
  GetCollectiveOffersSwrKeysProps,
  getCollectiveOffersSwrKeys,
} from '../getCollectiveOffersSwrKeys'

const props: GetCollectiveOffersSwrKeysProps = {
  isInTemplateOffersPage: false,
  isNewOffersAndBookingsActive: false,
  selectedOffererId: '1',
  urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
}

describe('getCollectiveOffersSwrKeys', () => {
  it('should return the correct offers list type', () => {
    expect(getCollectiveOffersSwrKeys(props)[0]).toEqual('getCollectiveOffers')

    expect(
      getCollectiveOffersSwrKeys({
        ...props,
        isNewOffersAndBookingsActive: true,
      })[0]
    ).toEqual('getCollectiveOffersBookable')

    expect(
      getCollectiveOffersSwrKeys({
        ...props,
        isNewOffersAndBookingsActive: true,
        isInTemplateOffersPage: true,
      })[0]
    ).toEqual('getCollectiveOffersTemplate')
  })

  it('should omit the page number in search filters', () => {
    expect(
      getCollectiveOffersSwrKeys({
        ...props,
        urlSearchFilters: { ...props.urlSearchFilters, page: 1 },
      })[1].page
    ).toBeUndefined()
  })

  it('should return the right offerer id', () => {
    expect(
      getCollectiveOffersSwrKeys({
        ...props,
        selectedOffererId: null,
      })[1].offererId
    ).toEqual('all')

    expect(
      getCollectiveOffersSwrKeys({
        ...props,
      })[1].offererId
    ).toEqual(props.selectedOffererId?.toString())
  })
})

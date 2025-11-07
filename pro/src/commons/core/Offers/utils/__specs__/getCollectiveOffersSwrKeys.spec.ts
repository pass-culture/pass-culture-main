import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'

import {
  type GetCollectiveOffersSwrKeysProps,
  getCollectiveOffersSwrKeys,
} from '../getCollectiveOffersSwrKeys'

const props: GetCollectiveOffersSwrKeysProps = {
  isInTemplateOffersPage: false,
  selectedOffererId: 1,
  urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
}

describe('getCollectiveOffersSwrKeys', () => {
  it('should return the correct offers list type', () => {
    expect(
      getCollectiveOffersSwrKeys({
        ...props,
      })[0]
    ).toEqual('getCollectiveOffersBookable')

    expect(
      getCollectiveOffersSwrKeys({
        ...props,
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

  it('should return the right offerer and venue ids', () => {
    expect(
      getCollectiveOffersSwrKeys({
        ...props,
      })[1]
    ).toMatchObject({
      offererId: '1',
      venueId: 'all',
    })

    expect(
      getCollectiveOffersSwrKeys({
        ...props,
        selectedVenueId: 2,
      })[1]
    ).toMatchObject({
      offererId: '1',
      venueId: '2',
    })
  })
})

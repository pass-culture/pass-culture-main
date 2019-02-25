import React from 'react'
import { shallow } from 'enzyme'
import RawOfferItem from '../RawOfferItem'

import mockedOffers from './offersMock'

describe('src | components | pages | Offers | RawOfferItem', () => {
  const dispatchMock = jest.fn()
  const initialProps = {
    dispatch: dispatchMock,
    offer: mockedOffers[0],
    location: {
      search: '?orderBy=offer.id+desc',
    },
  }

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const wrapper = shallow(<RawOfferItem {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
      dispatchMock.mockClear()
    })
  })

  describe('render', () => {
    describe('when offer is new', () => {
      // TO IMPLEMENT
    })
    describe('When group size', () => {
      // TO IMPLEMENT
    })
  })

  describe('functions', () => {
    describe('onDeactivateClick', () => {
      // when
      const wrapper = shallow(<RawOfferItem {...initialProps} />)
      wrapper.instance().onDeactivateClick()
      const expected = {
        config: {
          body: {
            isActive: false,
          },
          isMergingDatum: true,
          isMutaginArray: false,
          isMutatingDatum: true,
          normalizer: {
            event: {
              key: 'events',
              normalizer: {
                offers: 'offers',
              },
            },
            eventOccurrences: 'eventOccurrences',
            mediations: 'mediations',
            stocks: 'stocks',
            thing: {
              key: 'things',
              normalizer: {
                offers: 'offers',
              },
            },
            venue: {
              key: 'venues',
              normalizer: {
                managingOfferer: 'offerers',
              },
            },
          },
        },
        method: 'PATCH',
        path: 'offers/M4',
        type: 'REQUEST_DATA_PATCH_OFFERS/M4',
      }

      // then
      expect(dispatchMock.mock.calls[0][0]).toEqual(expected)
    })
  })
})

import { shallow } from 'enzyme'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'

import { recommendationNormalizer } from '../../../../utils/normalizers'
import SearchResultItem from '../SearchResultItem'

describe('src | components | pages | search | SearchResultItem', () => {
  let props

  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      history: {
        push: jest.fn(),
      },
      location: {
        pathname: '/recherche/resultats',
        search: '?categories=Applaudir',
      },
      recommendation: {
        id: 'QA',
        offer: {
          dateRange: [],
          name: 'sur la route des migrants ; rencontres à Calais',
          product: {
            offerType: {
              appLabel: 'Livres, cartes bibliothèque ou médiathèque',
            },
          },
        },
        offerId: 'X9',
        thumbUrl: 'http://localhost/storage/thumbs/products/QE',
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<SearchResultItem {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('onSuccessLoadRecommendationDetails()', () => {
    it('should push URL in history', () => {
      // given
      const wrapper = shallow(<SearchResultItem {...props} />)

      // when
      wrapper.instance().onSuccessLoadRecommendationDetails()

      // then
      const expectedUrl = `${props.location.pathname}/item/${props.recommendation.offerId}${props.location.search}`
      expect(props.history.push).toHaveBeenCalledWith(expectedUrl)
    })
  })

  describe('markSearchRecommendationsAsClicked()', () => {
    it('should dispatch the request data', () => {
      // given
      const wrapper = shallow(<SearchResultItem {...props} />)

      // when
      wrapper.instance().markSearchRecommendationsAsClicked()

      // then
      expect(props.dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/recommendations/${props.recommendation.id}`,
          body: { isClicked: true },
          handleSuccess: expect.any(Function),
          method: 'PATCH',
          normalizer: recommendationNormalizer,
        },
        type: `REQUEST_DATA_PATCH_/RECOMMENDATIONS/${props.recommendation.id}`,
      })
    })
  })

  describe('render()', () => {
    it('should have one item result details by default', () => {
      // given
      const wrapper = shallow(<SearchResultItem {...props} />)

      // when
      const img = wrapper.find('img').props()
      const h5 = wrapper.find('h5').props()
      const dotdotdot = wrapper.find(Dotdotdot).props()
      const recommendationDate = wrapper
        .find('.fs13')
        .last()
        .text()
      const first = wrapper
        .find('.fs13')
        .first()
        .text()

      // then
      expect(img.src).toBe('http://localhost/storage/thumbs/products/QE')
      expect(h5.title).toBe('sur la route des migrants ; rencontres à Calais')
      expect(dotdotdot.children).toBe(
        'sur la route des migrants ; rencontres à Calais'
      )
      expect(first).toBe('Livres, cartes bibliothèque ou médiathèque')
      expect(recommendationDate).toBe('permanent')
    })
  })
})

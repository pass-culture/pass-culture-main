import { shallow } from 'enzyme'
import React from 'react'

import RecommendationItem from '../RecommendationItem'

describe('src | components | pages | search | Result | RecommendationItem', () => {
  let props

  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      handleMarkSearchRecommendationsAsClicked: jest.fn(),
      offer: {
        dateRange: [],
        name: 'sur la route des migrants ; rencontres à Calais',
        offerType: {
          appLabel: 'Livres, cartes bibliothèque ou médiathèque',
        },
      },
      recommendation: {
        id: 'QA',
        offerId: 'X9',
        thumbUrl: 'http://localhost/storage/thumbs/products/QE',
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<RecommendationItem {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should have one item result details by default', () => {
      // given
      const wrapper = shallow(<RecommendationItem {...props} />)

      // when
      const img = wrapper.find('img').props()
      const h5 = wrapper.find('h5').props()
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
      expect(first).toBe('Livres, cartes bibliothèque ou médiathèque')
      expect(recommendationDate).toBe('permanent')
    })
  })
})

import React from 'react'
import { Link } from 'react-router-dom'
import { shallow } from 'enzyme'
import Dotdotdot from 'react-dotdotdot'

import SearchResultItem from '../SearchResultItem'
import state from '../../../../mocks/global_state_1'
import { selectRecommendations } from '../../../../selectors'

describe('src | components | pages | SearchResultItem', () => {
  const recommendations = selectRecommendations(state)

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        recommendation: recommendations[0],
      }

      // when
      const wrapper = shallow(<SearchResultItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    let props
    let wrapper
    describe.skip('with an event type recommendation with no dates', () => {
      // TODO Tester quels sont nos cas de figure...  Ou bien dans discovery
      // Un event avec une date fixe Le YYYY
    })
    describe('with an event type recommendation', () => {
      it('it should display item details', () => {
        props = {
          recommendation: recommendations[0],
        }
        wrapper = shallow(<SearchResultItem {...props} />)

        const linkUrl = wrapper.find(Link).props()
        const img = wrapper.find('img').props()
        const h5 = wrapper.find('h5').props()
        const dotdotdot = wrapper.find(Dotdotdot).props()
        const recommendationDate = wrapper.find('#recommendation-date').props()
        expect(linkUrl.to).toEqual('/decouverte/X9')
        expect(img.src).toEqual('http://localhost/storage/thumbs/things/QE')
        expect(dotdotdot.children).toEqual(
          'sur la route des migrants ; rencontres à Calais'
        )
        expect(recommendationDate.children).toEqual('permanent')
        expect(h5.title).toEqual(
          'sur la route des migrants ; rencontres à Calais'
        )
      })
    })
  })
})

import React from 'react'
import { Link } from 'react-router-dom'
import { shallow } from 'enzyme'
import Dotdotdot from 'react-dotdotdot'

import SearchResultItem from '../SearchResultItem'
import Thumb from '../../../layout/Thumb'
import state from './mocks/state'
import { selectRecommendations } from '../../../../selectors/recommendations'

describe.skip('src | components | pages | SearchResultItem', () => {
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
    describe('with an event type recommendation', () => {
      it('it should display item details with a permanent date', () => {
        props = {
          recommendation: recommendations[0],
        }
        wrapper = shallow(<SearchResultItem {...props} />)

        const linkUrl = wrapper.find(Link).props()
        const thumbUrl = wrapper.find(Thumb).props()
        const dotdotdot = wrapper.find(Dotdotdot).props()
        const span = wrapper.find('span').props()
        expect(linkUrl.to).toEqual('/decouverte/X9')
        expect(thumbUrl.src).toEqual(
          'http://localhost/storage/thumbs/things/QE'
        )
        expect(dotdotdot.children).toEqual(
          'sur la route des migrants ; rencontres à Calais'
        )
        expect(span.children).toEqual('permanent')
      })
    })
  })
})

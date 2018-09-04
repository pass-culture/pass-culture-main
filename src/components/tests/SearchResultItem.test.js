import React from 'react'
import { Link } from 'react-router-dom'
import { shallow } from 'enzyme'
import Dotdotdot from 'react-dotdotdot'

import SearchResultItem from '../SearchResultItem'
import Thumb from '../layout/Thumb'
import recommendationItems from './mocks/recommendationItems'
import { THUMBS_URL } from '../../utils/config'

describe('src | components | pages | SearchResultItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        recommendation: recommendationItems.event,
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
      it('it should display item details', () => {
        // NOTE Voir si ce n'est pas overkilled avec testcafe. Au moins ici au peut bouchonner.
        props = {
          recommendation: recommendationItems.event,
        }

        wrapper = shallow(<SearchResultItem {...props} />)

        const linkUrl = wrapper.find(Link).props()
        const thumbUrl = wrapper.find(Thumb).props()
        const dotdotdot = wrapper.find(Dotdotdot).props()

        expect(linkUrl.to).toEqual('/decouverte/AFUQ')
        expect(thumbUrl.src).toEqual(`${THUMBS_URL}/events/B9`)
        expect(dotdotdot.children).toEqual('Atelier Emploi niveau 1')
      })
    })
  })
})

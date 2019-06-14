import React from 'react'
import { shallow } from 'enzyme'

import Notification from '../Notification'

describe('src | components | layout | Notification', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(
        <Notification {...props}>
          <div>foo</div>
        </Notification>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('url type notification', () => {
      it('', () => {
        // given
        const props = {
          tag: "offerers",
          text: "Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)",
          type: "info",
          url: "/structures/AFPQ/lieux/creation",
          urlLabel: "Nouveau lieu"
        }

        // when
        const wrapper = shallow(
          <Notification {...props}/>
        )

        // then
        expect(wrapper.props()).toEqual('1')
      })

    })
  })
})

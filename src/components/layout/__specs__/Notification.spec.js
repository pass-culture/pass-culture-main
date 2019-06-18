import { Icon } from 'pass-culture-shared'
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
    describe('no venue yet notification', () => {
      it('should display info type with specific text and a link', () => {
        // given
        const props = {
          notification: {
            tag: "offerers",
            text: "Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)",
            type: "info",
            url: "/structures/AFPQ/lieux/creation",
            urlLabel: "Nouveau lieu"
          }
        }

        // when
        const wrapper = shallow(<Notification {...props}/>)
        const link = wrapper.find('a')

        // then
        const icon = wrapper.find(Icon)
        expect(icon).toHaveLength(1)
        expect(icon.prop('svg')).toBe('picto-info')
        expect(link.props().href).toEqual(props.notification.url)
        expect(link.text()).toEqual(props.notification.urlLabel)
      })
      it('should dispatch close ', () => {
        // given
        const dispatch = jest.fn()
        const props = {
          dispatch: dispatch,
          notification: {
            tag: "offerers",
            text: "Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)",
            type: "info",
            url: "/structures/AFPQ/lieux/creation",
            urlLabel: "Nouveau lieu"
          }
        }

        // when
        const wrapper = shallow(<Notification {...props}/>)

        // then
        const expected = {"type": "CLOSE_NOTIFICATION"}
        wrapper.find('button').simulate('click')
        expect(dispatch).toHaveBeenCalledWith(expected)
      })
    })
    describe('tooltip notification', () => {
      it('should display text', () => {
        // given
        const props = {
          notification: {
            tooltip: {
              place: 'bottom',
              tip: "<p>Il n'est pas possible de modifier le nom, l'addresse et la géolocalisation du lieu quand un siret est renseigné.</p>",
              type: 'info'
            }
          }
        }

        // when
        const wrapper = shallow(<Notification {...props}/>)
        const icon = wrapper.find(Icon)
        const spans = wrapper.find('span')

        // then
        expect(icon.prop('svg')).toBe('picto-echec')
        expect(spans.at(1).prop('data-tip')).toEqual(props.notification.tooltip.tip)
      })
    })
  })
})

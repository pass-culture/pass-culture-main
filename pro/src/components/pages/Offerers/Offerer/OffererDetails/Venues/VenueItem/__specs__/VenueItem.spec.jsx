/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt rtl "Gaël: migration from enzyme to RTL"
*/

import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Link, Router } from 'react-router-dom'

import VenueItem from '../VenueItem'

describe('src | components | pages | OffererCreation | VenueItem', () => {
  let props
  let history

  beforeEach(() => {
    props = {
      venue: {
        id: 'AAA',
        managingOffererId: 'ABC',
        name: 'fake name',
        publicName: null,
      },
    }
    history = createBrowserHistory()
  })

  describe('render', () => {
    describe('venue name link', () => {
      it('should render link to see venue details with venue name when no public name provided', () => {
        // given
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const venueName = wrapper.find('.name')
        const navLink = venueName.find(Link)

        // then
        expect(venueName.text()).toBe('fake name')
        expect(navLink.prop('id')).toBe('a-fake-name')
        expect(navLink.prop('to')).toBe('/structures/ABC/lieux/AAA')
      })

      it('should render link to see venue details with venue public name when public name provided', () => {
        // given
        props.venue.publicName = 'fake public name'

        // when
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const venueName = wrapper.find('.name')
        const navLink = venueName.find(Link)

        // then
        expect(venueName.text()).toBe('fake public name')
        expect(navLink.prop('id')).toBe('a-fake-public-name')
      })
    })

    describe('create new offer in the venue link', () => {
      it('should redirect to offer creation page', () => {
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const actions = wrapper.find('.actions')
        const navLink = actions.find(Link)

        // then
        expect(navLink.text()).toBe(' Créer une offre')
        expect(navLink.at(0).prop('to')).toBe('/offres/creation?lieu=AAA&structure=ABC')
      })
    })

    describe('see venue details link', () => {
      it('should redirect to venue details page', () => {
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const caret = wrapper.find('.caret')
        const navLink = caret.find(Link)

        // then
        expect(navLink.prop('to')).toBe('/structures/ABC/lieux/AAA')
      })
    })
  })
})

import React from 'react'
import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'

import VenueItem from '../VenueItem'
import { Router, NavLink } from 'react-router-dom'

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

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<VenueItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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
        const navLink = venueName.find(NavLink)

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
        const navLink = venueName.find(NavLink)

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
        const navLink = actions.find(NavLink)

        // then
        expect(navLink.text()).toBe(' Créer une offre')
        expect(navLink.at(0).prop('to')).toBe('/offres/creation?lieu=AAA&structure=ABC')
      })
    })

    describe('see all offers in one venue link', () => {
      it('should not be displayed if venue has no offers yet', () => {
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const actions = wrapper.find('.actions')
        const navLink = actions.find(NavLink)
        const actionsTypes = actions.find('li')

        // then
        expect(navLink.at(1)).toHaveLength(0)
        expect(actionsTypes.at(1).text()).toBe('0 offre')
      })

      it('should redirect to offers page', () => {
        props.venue.nOffers = 3
        const wrapper = mount(
          <Router history={history}>
            <VenueItem {...props} />
          </Router>
        )
        const actions = wrapper.find('.actions')
        const navLink = actions.find(NavLink)

        // then
        expect(navLink.at(1).text()).toBe('3 offres')
        expect(navLink.at(1).prop('to')).toBe('/offres?lieu=AAA&structure=ABC')
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
        const navLink = caret.find(NavLink)

        // then
        expect(navLink.prop('to')).toBe('/structures/ABC/lieux/AAA')
      })
    })
  })
})

import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import Venues from '../Venues'

describe('src | components | pages | OffererCreation | Venues', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: '5767Fdtre',
      venues: [],
      isVenueCreationAvailable: true,
    }
  })
  const mountReturnVenues = props => {
    const store = configureTestStore({ app: { logEvent: jest.fn() } })
    return mount(
      <Provider store={store}>
        <MemoryRouter>
          <Venues {...props} />
        </MemoryRouter>
      </Provider>
    )
  }

  describe('render', () => {
    it('should render a title link', () => {
      // given
      const wrapper = mountReturnVenues(props)

      // when
      const title = wrapper.find('h2')

      // then
      expect(title.text()).toBe('Lieux')
    })

    describe('create new venue link', () => {
      describe('when the venue creation is available', () => {
        it('should render a create venue link', () => {
          // given
          const wrapper = mountReturnVenues(props)

          // when
          const link = wrapper.find({ children: '+ Ajouter un lieu' })

          // then
          expect(link.first().prop('to')).toBe(
            '/structures/5767Fdtre/lieux/creation'
          )
        })
      })
      describe('when the venue creation is disabled', () => {
        it('should render a create venue link', () => {
          // given
          props.isVenueCreationAvailable = false
          const wrapper = mountReturnVenues(props)

          // when
          const link = wrapper.find({ children: '+ Ajouter un lieu' })

          // then
          expect(link.first().prop('to')).toBe('/erreur/indisponible')
        })
      })
    })
  })
})

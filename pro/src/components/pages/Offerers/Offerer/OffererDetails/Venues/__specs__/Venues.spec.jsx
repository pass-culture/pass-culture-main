import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
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
    return render(
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
      mountReturnVenues(props)

      // when
      const title = screen.getByRole('heading', { level: 2 })

      // then
      expect(title).toHaveTextContent('Lieux')
    })

    describe('create new venue link', () => {
      describe('when the venue creation is available', () => {
        it('should render a create venue link', () => {
          // given
          mountReturnVenues(props)

          // when
          const link = screen.getAllByRole('link')[0]

          // then
          expect(link).toHaveAttribute(
            'href',
            '/structures/5767Fdtre/lieux/creation'
          )
        })
      })
      describe('when the venue creation is disabled', () => {
        it('should render a create venue link', () => {
          // given
          props.isVenueCreationAvailable = false
          mountReturnVenues(props)

          // when
          const link = screen.getAllByRole('link')[0]

          // then
          expect(link).toHaveAttribute('href', '/erreur/indisponible')
        })
      })
    })
  })
})

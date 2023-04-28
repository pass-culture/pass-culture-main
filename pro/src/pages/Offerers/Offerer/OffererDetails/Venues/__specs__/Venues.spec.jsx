import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Venues from '../Venues'

describe('src | components | pages | OffererCreation | Venues', () => {
  let props
  const offererId = 1

  beforeEach(() => {
    props = {
      offererId: offererId,
      venues: [],
    }
  })
  const renderReturnVenues = (storeOverrides = {}) =>
    renderWithProviders(<Venues {...props} />, { storeOverrides })

  describe('render', () => {
    it('should render a title', () => {
      // given
      renderReturnVenues({
        features: {
          list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
        },
      })
      // when
      const title = screen.getByRole('heading', { level: 2 })

      // then
      expect(title).toHaveTextContent('Lieux')
    })

    describe('create new venue link', () => {
      describe('when the venue creation is available', () => {
        it('should render a create venue link', () => {
          // given
          renderReturnVenues({
            features: {
              list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
            },
          })
          // when
          const link = screen.getAllByRole('link')[0]

          // then
          expect(link).toHaveAttribute(
            'href',
            `/structures/${offererId}/lieux/creation`
          )
        })
      })
      describe('when the venue creation is disabled', () => {
        it('should render a create venue link', () => {
          // given
          renderReturnVenues()

          // when
          const link = screen.getAllByRole('link')[0]

          // then
          expect(link).toHaveAttribute('href', '/erreur/indisponible')
        })
      })
    })
  })
})

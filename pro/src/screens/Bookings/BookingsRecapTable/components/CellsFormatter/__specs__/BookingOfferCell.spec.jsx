import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import BookingOfferCell from '../BookingOfferCell'

const renderOfferCell = (props, store) =>
  render(
    <Provider store={store}>
      <BookingOfferCell {...props} />
    </Provider>
  )

describe('bookings offer cell', () => {
  describe('should always display', () => {
    let store

    beforeEach(() => {
      store = configureTestStore({})
    })

    it('offer name and isbn with a link to the offer when stock is a book', () => {
      // Given
      const props = {
        offer: {
          offerIdentifier: 'A0',
          offerIsbn: '97834567654',
          offerName: 'La Guitare pour les nuls',
          type: 'book',
          venueDepartmentCode: '93',
          offerIsEducational: false,
        },
      }

      // When
      renderOfferCell(props, store)

      // Then
      const isbn = screen.getByText('97834567654')
      expect(isbn).toBeInTheDocument()
      const title = screen.getByText('La Guitare pour les nuls')
      const title_link = title.closest('a')
      expect(title_link.href).toContain('offre/individuelle/A0')
      expect(title_link.target).toContain('_blank')
    })

    it('offer name with a link to the offer when stock is a thing', () => {
      // Given
      const props = {
        offer: {
          offerIdentifier: 'A1',
          offerName: 'Guitare acoustique',
          type: 'thing',
          venueDepartmentCode: '93',
          offerIsEducational: false,
        },
      }

      // When
      renderOfferCell(props, store)

      // Then
      const offer_name = screen.getByText('Guitare acoustique')
      const offer_name_link = offer_name.closest('a')
      expect(offer_name_link.href).toContain('offre/individuelle/A1')
      expect(offer_name_link.target).toContain('_blank')
    })

    it('offer name and event beginning datetime in venue timezone when stock is an event', () => {
      // Given
      const props = {
        offer: {
          eventBeginningDatetime: '2020-05-12T11:03:28.564687+04:00',
          offerIdentifier: 'A2',
          offerName: 'La danse des poireaux',
          type: 'event',
          venueDepartmentCode: '93',
          offerIsEducational: false,
        },
      }

      // When
      renderOfferCell(props, store)

      // Then
      expect(screen.getByText('12/05/2020 11:03')).toBeInTheDocument()
      const offer_name = screen.getByText('La danse des poireaux')
      const offer_name_link = offer_name.closest('a')
      expect(offer_name_link.href).toContain('offre/individuelle/A2')
      expect(offer_name_link.target).toContain('_blank')
    })
  })
})

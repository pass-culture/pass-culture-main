import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import BookingOfferCell from '../BookingOfferCell'

const renderOfferCell = props => render(<BookingOfferCell {...props} />)

describe('bookings offer cell', () => {
  describe('should always display', () => {
    it('offer name and isbn with a link to the offer when stock is a book', () => {
      // Given
      const props = {
        offer: {
          offer_identifier: 'A0',
          offer_isbn: '97834567654',
          offer_name: 'La Guitare pour les nuls',
          type: 'book',
          venue_department_code: '93',
        },
      }

      // When
      renderOfferCell(props)

      // Then
      const isbn = screen.getByText('97834567654')
      const isbn_link = isbn.closest('a')
      expect(isbn_link.href).toContain('offres/A0')
      expect(isbn_link.target).toContain('_blank')
    })

    it('offer name with a link to the offer when stock is a thing', () => {
      // Given
      const props = {
        offer: {
          offer_identifier: 'A1',
          offer_name: 'Guitare acoustique',
          type: 'thing',
          venue_department_code: '93',
        },
      }

      // When
      renderOfferCell(props)

      // Then
      const offer_name = screen.getByText('Guitare acoustique')
      const offer_name_link = offer_name.closest('a')
      expect(offer_name_link.href).toContain('offres/A1')
    })

    it('offer name and event beginning datetime in venue timezone when stock is an event', () => {
      // Given
      const props = {
        offer: {
          event_beginning_datetime: '2020-05-12T11:03:28.564687+04:00',
          offer_identifier: 'A2',
          offer_name: 'La danse des poireaux',
          type: 'event',
          venue_department_code: '93',
        },
      }

      // When
      renderOfferCell(props)

      // Then
      expect(screen.getByText('12/05/2020 11:03')).toBeInTheDocument()
      const offer_name = screen.getByText('La danse des poireaux')
      const offer_name_link = offer_name.closest('a')
      expect(offer_name_link.href).toContain('offres/A2')
    })
  })
})

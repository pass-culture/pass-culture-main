import { mount, shallow } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import BookingsList from '../BookingsList/BookingsList'
import MyBookingsLists from '../MyBookingsLists'

describe('src | components | MyBookingsLists', () => {
  let props

  beforeEach(() => {
    props = {
      finishedAndUsedAndCancelledBookings: [],
      upComingBookings: [],
      bookingsOfTheWeek: [],
    }
  })

  it('should display the title "Réservations"', () => {
    // When
    const wrapper = shallow(<MyBookingsLists {...props} />)

    // Then
    const title = wrapper.find('h1').find({ children: 'Réservations' })
    expect(title).toHaveLength(1)
  })

  describe('when I have no bookings', () => {
    it('should display a button that redirects to home page', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/reservations']}>
          <MyBookingsLists {...props} />
        </MemoryRouter>
      )

      // then
      const redirectButton = wrapper.find('a')
      expect(redirectButton.text()).toBe('Lance-toi !')
      expect(redirectButton.prop('href')).toBe('/')
    })

    it('should display a description text', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/favoris']}>
          <MyBookingsLists {...props} />
        </MemoryRouter>
      )

      // then
      const descriptionText = wrapper.find({
        children: 'Dès que tu auras réservé une offre, tu la retrouveras ici.',
      })
      expect(descriptionText).toHaveLength(1)
    })
  })

  describe('when I have just booking of the week', () => {
    it('should render booking of the week', () => {
      // given
      props.isEmpty = false
      props.bookingsOfTheWeek = [
        {
          id: 'b1',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      const title = wrapper.find({ children: 'Réservations' })
      const thisWeekSentence = wrapper.find({ children: 'Cette semaine' })
      const bookingsList = wrapper.find(BookingsList)
      const sentence = wrapper.find({
        children:
          'Le code de réservation à 6 caractères est ta preuve d’achat. Ne communique ce code qu’au moment du retrait de ta commande.',
      })
      expect(title).toHaveLength(1)
      expect(thisWeekSentence).toHaveLength(1)
      expect(bookingsList).toHaveLength(1)
      expect(sentence).toHaveLength(1)
    })
  })

  describe('when I have just upcoming booking', () => {
    it('should render upcoming booking', () => {
      // given
      props.isEmpty = false
      props.upComingBookings = [
        {
          id: 'b1',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      const title = wrapper.find({ children: 'Réservations' })
      const sentence = wrapper.find({
        children:
          'Le code de réservation à 6 caractères est ta preuve d’achat. Ne communique ce code qu’au moment du retrait de ta commande.',
      })
      const toComeSentence = wrapper.find({ children: 'À venir' })
      const bookingsList = wrapper.find(BookingsList)
      expect(title).toHaveLength(1)
      expect(sentence).toHaveLength(1)
      expect(toComeSentence).toHaveLength(1)
      expect(bookingsList).toHaveLength(1)
    })
  })

  describe('when I have just finished/cancelled bookings', () => {
    it('should render finished/used/cancelled bookings', () => {
      // given
      props.isEmpty = false
      props.finishedAndUsedAndCancelledBookings = [
        {
          id: 'b1',
        },
        {
          id: 'b2',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      const title = wrapper.find({ children: 'Réservations' })
      const sentence = wrapper.find({
        children:
          'Le code de réservation à 6 caractères est ta preuve d’achat. Ne communique ce code qu’au moment du retrait de ta commande.',
      })
      const finishedSentence = wrapper.find({ children: 'Terminées' })
      const bookingsList = wrapper.find(BookingsList)
      expect(title).toHaveLength(1)
      expect(sentence).toHaveLength(1)
      expect(finishedSentence).toHaveLength(1)
      expect(bookingsList).toHaveLength(1)
    })
  })
})

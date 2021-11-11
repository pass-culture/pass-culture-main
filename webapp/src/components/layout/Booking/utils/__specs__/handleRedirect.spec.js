import handleRedirect from '../handleRedirect'

describe('src | components | booking | utils | handleRedirect', () => {
  describe('when navigating from my bookings', () => {
    it('should redirect to booking detail on my reservations view', () => {
      // given
      const match = {
        url: '/reservations/details/AJPQ/reservation',
        params: {
          bookingId: 'ABC1',
        },
      }
      const location = {}

      // when
      const result = handleRedirect(match, location)

      // then
      expect(result).toBe('/reservations/details/ABC1')
    })
  })

  describe('when navigating from my favorites', () => {
    it('should redirect to booking detail to my favorites view', () => {
      // given
      const match = {
        url: '/favoris/details/AUVQ/AQ7A/reservation',
        params: {
          bookingId: undefined,
        },
      }
      const location = {}

      // when
      const result = handleRedirect(match, location)

      // then
      expect(result).toBe('/favoris/details/AUVQ/AQ7A')
    })
  })

  describe('when navigating from discovery', () => {
    it('should redirect to booking detail on discovery view', () => {
      // given
      const match = {
        url: '/decouverte/AUVQ/AQ7A/details/reservation',
        params: {
          bookingId: undefined,
        },
      }
      const location = {}

      // when
      const result = handleRedirect(match, location)

      // then
      expect(result).toBe('/decouverte/AUVQ/AQ7A/details')
    })
  })

  describe('when navigating from search', () => {
    it('should redirect to booking detail on previous search view', () => {
      // given
      const match = {
        url: '/recherche/details/AUVQ/reservation',
        params: {
          bookingId: undefined,
        },
      }
      const location = {
        search: '?mots-cles="librairie"&page=3',
      }

      // when
      const result = handleRedirect(match, location)

      // then
      expect(result).toBe('/recherche/details/AUVQ?mots-cles="librairie"&page=3')
    })
  })
})

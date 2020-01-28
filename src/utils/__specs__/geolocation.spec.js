import {
  computeDistanceInMeters, computeToAroundLatLng,
  getHumanizeRelativeDistance,
  humanizeDistance,
} from '../geolocation'

describe('src | utils | geolocation', () => {
  describe('getHumanizeRelativeDistance()', () => {
    describe('when the user is not geolocalized and the offer address is provided', () => {
      it('should return "-"', () => {
        // given
        const venueLatitude = 48.92763
        const venueLongitude = 2.49043

        // when
        const distance = getHumanizeRelativeDistance(venueLatitude, venueLongitude)

        // then
        expect(distance).toBe('-')
      })
    })

    describe('when the user is geolocalized and the offer address is provided', () => {
      it('should return 13 km', () => {
        // given
        const venueLatitude = 48.92763
        const venueLongitude = 2.49043
        const userLatitude = 48.863654499999996
        const userLongitude = 2.3371120999999997

        // when
        const distance = getHumanizeRelativeDistance(
          venueLatitude,
          venueLongitude,
          userLatitude,
          userLongitude
        )

        // then
        expect(distance).toBe('13 km')
      })
    })

    describe('when its a digital offer', () => {
      it('should return "-"', () => {
        // given
        const venueLatitude = null
        const venueLongitude = null
        const userLatitude = 48.863654499999996
        const userLongitude = 2.3371120999999997

        // when
        const distance = getHumanizeRelativeDistance(
          venueLatitude,
          venueLongitude,
          userLatitude,
          userLongitude
        )

        // then
        expect(distance).toBe('-')
      })
    })
  })

  describe('computeDistanceInMeters()', () => {
    it('should return the difference between two geolocalized points', () => {
      // given
      const latitudeA = -48.92763
      const longitudeA = 2.49043
      const latitudeB = 58.92763
      const longitudeB = 12.49043

      // when
      const distance = computeDistanceInMeters(latitudeA, longitudeA, latitudeB, longitudeB)

      // then
      expect(distance).toBe(12040943.568007572)
    })
  })

  describe('humanizeDistance()', () => {
    describe('when raw distance is less than 30', () => {
      it('should return "10 m"', () => {
        // given
        const rawDistance = 10

        // when
        const distance = humanizeDistance(rawDistance)

        // then
        expect(distance).toBe('10 m')
      })
    })

    describe('when raw distance is less than 100', () => {
      it('should return "50 m"', () => {
        // given
        const rawDistance = 50

        // when
        const distance = humanizeDistance(rawDistance)

        // then
        expect(distance).toBe('50 m')
      })
    })

    describe('when raw distance is less than 1000', () => {
      it('should return "500 m"', () => {
        // given
        const rawDistance = 500

        // when
        const distance = humanizeDistance(rawDistance)

        // then
        expect(distance).toBe('500 m')
      })
    })

    describe('when raw distance is less than 5000', () => {
      it('should return "2.5 km"', () => {
        // given
        const rawDistance = 2500

        // when
        const distance = humanizeDistance(rawDistance)

        // then
        expect(distance).toBe('2.5 km')
      })
    })

    describe('when raw distance is more than 5000', () => {
      it('should return "13 km"', () => {
        // given
        const rawDistance = 12500

        // when
        const distance = humanizeDistance(rawDistance)

        // then
        expect(distance).toBe('13 km')
      })
    })
  })

  describe('computeToAroundLatLng', () => {
    it('should return computed value when latitude and longitude are provided', () => {
      // given
      const geolocation = {
        latitude: 42,
        longitude: 43
      }

      // when
      const result = computeToAroundLatLng(geolocation)

      // then
      expect(result).toStrictEqual('42, 43')
    })

    it('should return empty value when latitude and longitude are not provided', () => {
      // given
      const geolocation = {
        latitude: null,
        longitude: null
      }

      // when
      const result = computeToAroundLatLng(geolocation)

      // then
      expect(result).toStrictEqual('')
    })
  })
})

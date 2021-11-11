import { buildGeolocationFilter } from '../buildGeolocationFilter'
import { GEOLOCATION_CRITERIA } from '../../../../components/pages/search/Criteria/criteriaEnums'
import { AppSearchFields } from '../../constants'

const geolocation = {
  latitude: 42,
  longitude: 43,
}

const baseParams = {
  aroundRadius: 10,
  locationType: GEOLOCATION_CRITERIA.AROUND_ME,
  geolocation,
}

describe('buildGeolocationFilter', () => {
  it('should not fetch with geolocation coordinates when latitude and longitude are not valid', () => {
    const params = { ...baseParams, geolocation: null }
    expect(buildGeolocationFilter(params)).toStrictEqual([])
  })

  it('should fetch offers with geolocation coordinates, when latitude, longitude are provided and search is not around me', () => {
    const params = { ...baseParams, locationType: GEOLOCATION_CRITERIA.EVERYWHERE }
    expect(buildGeolocationFilter(params)).toStrictEqual([])
  })

  it('should fetch offers with geolocation coordinates, when latitude, longitude and radius are provided and search is around me', () => {
    const params = { ...baseParams, aroundRadius: 135, searchAround: true }
    expect(buildGeolocationFilter(params)).toStrictEqual([
      {
        [AppSearchFields.venue_position]: {
          center: '42, 43',
          distance: 135,
          unit: 'km',
        },
      },
    ])
  })

  it('should fetch offers with geolocation coordinates, when latitude, longitude, search is around me, and radius equals zero', () => {
    const params = { ...baseParams, aroundRadius: 0, searchAround: true }
    expect(buildGeolocationFilter(params)).toStrictEqual([
      {
        [AppSearchFields.venue_position]: {
          center: '42, 43',
          distance: 1,
          unit: 'm',
        },
      },
    ])
  })

  it('should fetch offers with geolocation coordinates, when latitude, longitude, search is around me, and radius is null', () => {
    const params = { ...baseParams, aroundRadius: null }
    expect(buildGeolocationFilter(params)).toStrictEqual([])
  })

  it('should fetch offers with no geolocation filter if search is not around me or a place', () => {
    const params = { ...baseParams, searchAround: false }
    expect(buildGeolocationFilter(params)).toStrictEqual([])
  })
})

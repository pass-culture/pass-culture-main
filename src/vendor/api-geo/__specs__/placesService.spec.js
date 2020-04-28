import { fetchPlaces } from '../placesService'
import fetch from 'jest-fetch-mock'

describe('vendor | api-geo | placesService', () => {
  it('should return places from searched keywords', async () => {
    // given
    const address = '34 avenue opéra'
    const payload = {
      features: [{
        geometry: {
          coordinates: [40, 41]
        },
        properties: {
          city: 'Paris',
          context: '75, Paris, Ile-De-France',
          label: '34 avenue opéra'
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        departmentCode: '75',
        department: 'Paris',
        label: '34 avenue opéra',
        region: 'Ile-De-France'
      },
      geolocation: { 'latitude': 40, 'longitude': 41 },
      name: 'Paris'
    }])
  })

  it('should return places from searched keywords when some information are empty', async () => {
    // given
    const address = '34 avenue opéra'
    const payload = {
      features: [{
        geometry: {
          coordinates: [40, 41]
        },
        properties: {
          city: 'Paris',
          context: '',
          label: ''
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        departmentCode: '',
        department: '',
        label: '',
        region: ''
      },
      geolocation: { 'latitude': 40, 'longitude': 41 },
      name: 'Paris'
    }])
  })

  it('should return no places when error is triggered', async () => {
    // given
    const address = '34 avenue opéra'
    fetch.mockReject()

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([])
  })
})

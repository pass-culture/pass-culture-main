import { fetchPlaces } from '../placesService'
import fetch from 'jest-fetch-mock'
import typeEnum from '../typeEnum'

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
          label: '34 avenue opéra',
          type: typeEnum.LOCALITY
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        city: 'Paris',
        department: 'Paris',
      },
      geolocation: { 'latitude': 41, 'longitude': 40 },
      name: {
        long: 'Paris',
        short: 'Paris'
      }
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
          label: '',
          type: typeEnum.LOCALITY
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        city: 'Paris',
        department: '',
      },
      geolocation: { 'latitude': 41, 'longitude': 40 },
      name: {
        long: 'Paris',
        short: 'Paris'
      }
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

  it('should return places from searched keywords using info from name when it is a street', async () => {
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
          label: '',
          name: '34 avenue opéra',
          type: typeEnum.STREET
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        city: 'Paris',
        department: '',
      },
      geolocation: { 'latitude': 41, 'longitude': 40 },
      name: {
        long: '34 avenue opéra, Paris',
        short: '34 avenue opéra'
      }
    }])
  })

  it('should return places from searched keywords using info from name when it is an house number', async () => {
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
          label: '',
          name: '34 avenue opéra',
          type: typeEnum.HOUSE_NUMBER
        }
      }]
    }
    fetch.mockResponse(JSON.stringify(payload, { status: 200 }))

    // when
    const results = await fetchPlaces({ address })

    // then
    expect(results).toStrictEqual([{
      extraData: {
        city: 'Paris',
        department: '',
      },
      geolocation: { 'latitude': 41, 'longitude': 40 },
      name: {
        long: '34 avenue opéra, Paris',
        short: '34 avenue opéra'
      }
    }])
  })
})

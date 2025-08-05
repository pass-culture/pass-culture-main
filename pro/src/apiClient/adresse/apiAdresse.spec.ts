import { type Mock, vi } from 'vitest'
import { getDataFromAddress, getDataFromAddressParts } from './apiAdresse'
import { AdresseApiJson, FeaturePropertyType } from './types'

const mockApiResponse: Partial<AdresseApiJson> = {
  type: 'FeatureCollection',
  version: 'draft',
  features: [
    {
      geometry: {
        coordinates: [2.4, 48.9],
      },
      properties: {
        name: '15 Rue des Tests',
        city: 'Paris',
        id: '00000_0000_00000',
        label: '15 Rue des Tests 75001 Paris',
        postcode: '75001',
        type: 'housenumber' as FeaturePropertyType,
        citycode: '75056',
        context: 'Paris, Île-de-France',
        district: '1er Arrondissement',
        housenumber: '15',
        importance: 0.6,
        score: 0.98,
        street: 'Rue des Tests',
        x: 2.4,
        y: 48.9,
      },
    },
  ],
}

const mockEmptyApiResponse: Partial<AdresseApiJson> = {
  type: 'FeatureCollection',
  version: 'draft',
  features: [],
}

const mockCityApiResponse: Partial<AdresseApiJson> = {
  type: 'FeatureCollection',
  version: 'draft',
  features: [
    {
      geometry: {
        coordinates: [2.4, 48.9],
      },
      properties: {
        name: 'Paris',
        city: 'Paris',
        id: '11111_1111_11111',
        label: 'Paris',
        postcode: '75001',
        type: 'municipality' as FeaturePropertyType,
        citycode: '75056',
        context: 'Île-de-France',
        district: '',
        housenumber: '',
        importance: 1,
        score: 1,
        street: '',
        x: 2.4,
        y: 48.9,
      },
    },
  ],
}

describe('apiAdresse', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('getDataFromAddressParts', () => {
    it('should return formatted address data when address is found', async () => {
      ;(global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await getDataFromAddressParts(
        '15 Rue des Tests',
        'Paris',
        '75001'
      )

      expect(result).toEqual([
        {
          address: '15 Rue des Tests',
          city: 'Paris',
          id: '00000_0000_00000',
          latitude: 48.9,
          longitude: 2.4,
          label: '15 Rue des Tests 75001 Paris',
          postalCode: '75001',
          inseeCode: '75056',
        },
      ])
    })

    it('should fallback to city search when no address is found', async () => {
      ;(global.fetch as Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockEmptyApiResponse),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockCityApiResponse),
        })

      const result = await getDataFromAddressParts(
        '15 Rue Inexistante',
        'Paris',
        '75001'
      )

      expect(result).toEqual([
        {
          address: 'Paris',
          city: 'Paris',
          id: '11111_1111_11111',
          latitude: 48.9,
          longitude: 2.4,
          label: 'Paris',
          postalCode: '75001',
          inseeCode: '75056',
        },
      ])
    })

    it('should throw an error when API request fails', async () => {
      ;(global.fetch as Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        url: 'test-url',
      })

      await expect(
        getDataFromAddressParts('15 Rue des Tests', 'Paris', '75001')
      ).rejects.toThrow('Échec de la requête test-url, code: 500')
    })
  })

  describe('getDataFromAddress', () => {
    it('should return formatted address data with default options', async () => {
      ;(global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await getDataFromAddress('15 Rue des Tests')

      expect(result).toEqual([
        {
          address: '15 Rue des Tests',
          city: 'Paris',
          id: '00000_0000_00000',
          latitude: 48.9,
          longitude: 2.4,
          label: '15 Rue des Tests 75001 Paris',
          postalCode: '75001',
          inseeCode: '75056',
        },
      ])
    })

    it('should filter results by type when onlyTypes is specified', async () => {
      const mixedResponse: Partial<AdresseApiJson> = {
        type: 'FeatureCollection',
        version: 'draft',
        features: [
          {
            ...mockApiResponse.features![0],
            properties: {
              ...mockApiResponse.features![0].properties,
              type: 'street' as FeaturePropertyType,
            },
          },
          mockApiResponse.features![0],
        ],
      }

      ;(global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mixedResponse),
      })

      const result = await getDataFromAddress('15 Rue des Tests', {
        onlyTypes: ['housenumber'],
      })

      expect(result).toHaveLength(1)
      expect(result[0].address).toBe('15 Rue des Tests')
    })

    it('should respect custom limit parameter', async () => {
      ;(global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      await getDataFromAddress('15 Rue des Tests', { limit: 10 })

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=10')
      )
    })
  })
})

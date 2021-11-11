import { getRecommendationEndpoint } from './useRecommendedHits'

jest.mock('../../../../utils/config', () => ({
  RECOMMENDATION_ENDPOINT: 'endpoint',
  RECOMMENDATION_TOKEN: 'token',
}))

describe('getRecommendationEndpoint', () => {
  it('should return endpoint only for connected users', () => {
    expect(getRecommendationEndpoint(undefined, null)).toBeUndefined()
    expect(getRecommendationEndpoint(20, null)).toBe('endpoint/recommendation/20?token=token')
  })
  it('should format recommendation with position if available', () => {
    expect(getRecommendationEndpoint(20, null)).toBe('endpoint/recommendation/20?token=token')
    expect(getRecommendationEndpoint(20, { latitude: 20, longitude: 31.2 })).toBe(
      'endpoint/recommendation/20?token=token&longitude=31.2&latitude=20'
    )
  })
})

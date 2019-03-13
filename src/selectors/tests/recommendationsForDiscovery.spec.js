import selectRecommendationsForDiscovery from '../recommendationsForDiscovery'
import { selectRecommendations } from '../recommendations'
import { ROOT_PATH } from '../../utils/config'

jest.mock('../recommendations')
describe('selectRecommendationsForDiscovery', () => {
  it('should return an array of 1 element with just the fake end reco if there are no recommendations', () => {
    // given
    selectRecommendations.mockReturnValue([])

    const state = {
      data: {
        recommendations: [],
      },
    }

    // when
    const result = selectRecommendationsForDiscovery(state)

    // then
    expect(result.length).toEqual(1)
    expect(result[0].mediation.firstThumbDominantColor).toEqual([205, 54, 70])
    expect(result[0].mediation.frontText).toEqual(
      'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.'
    )
    expect(result[0].mediation.id).toEqual('fin')
    expect(result[0].mediation.thumbCount).toEqual(1)
    expect(result[0].mediation.thumbUrls).toEqual([
      `${ROOT_PATH}/splash-finReco@2x.png`,
    ])
    expect(result[0].mediation.tutoIndex).toEqual(-1)
    expect(result[0].mediationId).toEqual('fin')
    expect(result[0].uniqId).toEqual('tuto_-1')
  })

  it('should return an array of 2 elements with one recommendation with the fake end reco at the end of array', () => {
    // given
    selectRecommendations.mockReturnValue([{ id: 'A1' }])

    const state = {
      data: {
        recommendations: [{ id: 'A1' }],
      },
    }

    // when
    const result = selectRecommendationsForDiscovery(state)

    // then
    expect(result.length).toEqual(2)
    expect(result[1].uniqId).toEqual('tuto_-1')
  })
})

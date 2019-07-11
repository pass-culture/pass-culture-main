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
    expect(result).toHaveLength(1)
    expect(result[0].mediation.firstThumbDominantColor).toStrictEqual([205, 54, 70])
    expect(result[0].mediation.frontText).toStrictEqual(
      'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.'
    )
    expect(result[0].mediation.id).toStrictEqual('fin')
    expect(result[0].mediation.thumbCount).toStrictEqual(1)
    expect(result[0].thumbUrl).toStrictEqual(`${ROOT_PATH}/splash-finReco@2x.png`)
    expect(result[0].mediation.tutoIndex).toStrictEqual(-1)
    expect(result[0].mediationId).toStrictEqual('fin')
    expect(result[0].uniqId).toStrictEqual('tuto_-1')
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
    expect(result).toHaveLength(2)
    expect(result[1].uniqId).toStrictEqual('tuto_-1')
  })
})

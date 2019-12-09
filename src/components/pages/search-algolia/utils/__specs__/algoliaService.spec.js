import { fetch } from '../algoliaService'
import { searchedResults } from '../utils'

describe('service | algolia', () => {
  it('should return an array containers offers with number of results', () => {
    // given
    const keywords = 'un super livre'

    // when
    const results = fetch(keywords)

    // then
    expect(results).toStrictEqual(searchedResults)
  })
})

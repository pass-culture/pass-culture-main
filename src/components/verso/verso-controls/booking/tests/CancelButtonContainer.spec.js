// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/booking/tests/CancelButtonContainer.spec.js --watch
import { createBrowserHistory } from 'history'

import { mapStateToProps } from '../CancelButtonContainer'

describe('src | components | verso | verso-controls | booking | CancelButtonContainer', () => {
  it('returns a composed object', () => {
    // given
    const history = createBrowserHistory()
    const location = { search: '?a_search=string' }
    const booking = {
      isCancelled: false,
      stock: { price: 1 },
    }
    const state = {}
    const props = { booking, history, location }

    // when
    const result = mapStateToProps(state, props)

    // then
    const expected = {
      history,
      isCancelled: false,
      locationSearch: location.search,
      priceValue: 1,
    }
    expect(result).toStrictEqual(expected)
  })
})

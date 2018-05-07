import { createSelector } from 'reselect'

import getSource from '../getters/source'
import { THUMBS_URL } from '../utils/config'

export default createSelector(
  state => state.data.offers,
  (offers = []) =>
    offers && offers.map(o =>
      Object.assign(
        {
          source: getSource(o)
        },
        o
      )
    )
)

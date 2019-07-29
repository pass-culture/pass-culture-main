import { createSelector } from 'reselect'

const selectDigitalOffers = createSelector(
  state => state.data.offers || [],
  offers => offers.filter(offer => offer.isDigital === true)
)

export default selectDigitalOffers

import { createSelector } from 'reselect'

const removedLocalClasses = [
  'SpreadsheetExpVenues',
  'SpreadsheetExpOffers',
  'TiteLiveOffers',
  'TiteLiveVenues',
  'TiteLiveThings',
  'TiteLiveBookThumbs',
  'TiteLiveBookDescriptions'
]

export default createSelector(
  state => state.data.providers,
  providers => providers
    .filter(p => !removedLocalClasses.includes(p.localClass))
    .sort((p1, p2) => p1.localClass - p2.localClass)
)

import createCachedSelector from 're-reselect';

const removedLocalClasses = [
  'SpreadsheetExpVenues',
  'SpreadsheetExpOffers',
  'TiteLiveVenues',
  'TiteLiveThings',
  'TiteLiveBookThumbs',
  'TiteLiveBookDescriptions'
]

export default createCachedSelector(
  state => state.data.providers,
  providers => providers
    .filter(p => !removedLocalClasses.includes(p.localClass))
    .sort((p1, p2) => p1.localClass - p2.localClass)
)(() => '')

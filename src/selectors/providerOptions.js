import { createSelector } from 'reselect'

const removedLocalClasses = [
  'SpreadsheetExpVenues',
  'SpreadsheetExpOffers',
  'TiteLiveVenues',
  'TiteLiveThings',
  'TiteLiveBookThumbs',
  'TiteLiveBookDescriptions'
]


export default createSelector(
  state => state.data.providers,
  providers => {
    if (!providers) {
      return
    }

    const filteredProviders = providers.filter(p =>
       !removedLocalClasses.includes(p.localClass))

    filteredProviders.sort((p1, p2) => p1.localClass - p2.localClass)

    return filteredProviders.map(p => ({ label: p.name, value: p.id }))
  }
)

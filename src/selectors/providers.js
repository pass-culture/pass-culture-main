import { createSelector } from 'reselect'

import {resolveDataCollection} from '../utils/resolvers'

const removedLocalClasses = [
  'OpenAgendaOffers',
  'SpreadsheetExpThingOffers',
  'SpreadsheetExpVenues',
  'SpreadsheetExpOffers',
  'SpreadsheetOffers',
  'TiteLiveOffers',
  'TiteLiveVenues',
  'TiteLiveThings',
  'TiteLiveBookThumbs',
  'TiteLiveBookDescriptions'
]

export default createSelector(
  state => state.data.providers,
  providers => resolveDataCollection(providers, 'providers')
    .filter(p => !removedLocalClasses.includes(p.localClass))
    .sort((p1, p2) => p1.localClass - p2.localClass)
)

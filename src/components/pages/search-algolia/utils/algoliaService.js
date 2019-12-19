import {searchedResults} from './utils'

export const fetch = (keywords = '') => {
  if (!keywords) {
    return
  }
  return searchedResults
}

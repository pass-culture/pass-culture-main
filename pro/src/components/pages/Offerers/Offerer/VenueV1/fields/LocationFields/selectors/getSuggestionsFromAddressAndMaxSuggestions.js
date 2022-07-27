import { createCachedSelector } from 're-reselect'

import fetchAddressData from '../utils/fetchAddressData'

function mapArgsToCacheKey(address, maxSuggestions) {
  return `${address || ''}/${maxSuggestions || ''}`
}

const getSuggestionsFromAddressAndMaxSuggestions = createCachedSelector(
  address => address,
  (address, maxSuggestions) => maxSuggestions,
  async (address, maxSuggestions) => {
    const wordsCount = address.split(/\s/).filter(v => v).length
    if (wordsCount < 2) return { data: [] }
    const addressUrl = `https://api-adresse.data.gouv.fr/search/?limit=${maxSuggestions}&q=${address}`
    try {
      const data = await fetchAddressData(addressUrl)
      return { data }
    } catch (e) {
      const error = 'Impossible de vérifier l’adresse saisie.'
      return { error }
    }
  }
)(mapArgsToCacheKey)

export default getSuggestionsFromAddressAndMaxSuggestions

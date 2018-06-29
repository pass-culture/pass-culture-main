import createOffererSelector from '../createOfferer'
import state from './mockState'

describe('createOffererSelector', () => {
  it('should select the global state', () => {
    const expected = {
      "id": "AE",
      "address": "41 Boulevard de Strasbourg",
      "city": "AULNAY SOUS BOIS",
      "dateCreated": "2018-06-29T11:44:01.308417Z",
      "dateModifiedAtLastProvider": "2018-02-01T14:47:00Z",
      "dehumanizedId": 1,
      "dehumanizedLastProviderId": 7,
      "firstThumbDominantColor": null,
      "idAtProviders": "2949",
      "isActive": true,
      "isValidated": true,
      "lastProviderId": "A4",
      "modelName": "Offerer",
      "nOccasions": 188,
      "name": "Folies d'encre Aulnay-sous-Bois",
      "postalCode": "93600",
      "siren": "302559178",
      "thumbCount": 0,
      "managedVenuesIds": [
        "BQ",
        "AE"
      ]
    }
    const offererId = "AE"
    const selector = createOffererSelector()
    expect(selector(state, offererId)).toEqual(expected)
  })
})

import state from '../../../utils/mocks/state'
import { mapStateToProps } from '../OfferersContainer'

describe('src | components | pages | Offerers | OfferersContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {}

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        "offerers": [{
          "address": "RUE DES SAPOTILLES",
          "bic": "QSDFGH8Z566",
          "city": "Cayenne",
          "dateCreated": "2019-03-07T10:39:23.560414Z",
          "dateModifiedAtLastProvider": "2019-03-07T10:39:57.823508Z",
          "firstThumbDominantColor": null,
          "iban": "FR7630001007941234567890185",
          "id": "BA",
          "idAtProviders": null,
          "isActive": true,
          "isValidated": true,
          "lastProviderId": null,
          "modelName": "Offerer",
          "nOffers": 5,
          "name": "Bar des amis",
          "postalCode": "97300",
          "siren": "222222233",
          "thumbCount": 0,
          "validationToken": null
        }, {
          "address": "RUE DES POMMES ROSAS",
          "city": "Cayenne",
          "dateCreated": "2019-03-07T10:39:23.560414Z",
          "dateModifiedAtLastProvider": "2019-03-07T10:39:57.843884Z",
          "firstThumbDominantColor": null,
          "id": "CA",
          "idAtProviders": null,
          "isActive": true,
          "isValidated": false,
          "lastProviderId": null,
          "modelName": "Offerer",
          "nOffers": 10,
          "name": "Cinéma du coin",
          "postalCode": "97300",
          "siren": "222222232",
          "thumbCount": 0,
          "validationToken": "w3hDQgjYRIyYTxOYY08nwgH3BzI"
        }],
        "pendingOfferers": []
      }
      expect(result).toEqual(expected)
    })
  })
})

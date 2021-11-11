/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

import { mapStateToProps, mapDispatchToProps } from '../../OffererDetails/OffererDetailsContainer'

jest.mock('redux-saga-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
    createDataReducer: jest.fn(),
  }
})

describe('src | components | pages | Offerer | OffererDetails | OffererDetailsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'TY56er',
            },
          ],
          userOfferers: [
            {
              id: 'AEKQ',
              modelName: 'UserOfferer',
              offererId: 'AGH',
              rights: 'admin',
              userId: 'TY56er',
            },
          ],
          offerers: [
            {
              id: 'AGH',
              name: 'Gaumont cinéma',
              bic: 'bic',
              iban: 'iban',
              siren: '256712456',
              address: '256, rue des mimosas',
            },
          ],
          venues: [],
        },
      }
      const ownProps = {
        match: {
          params: {
            offererId: 'AGH',
          },
        },
      }
      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        currentUser: {
          id: 'TY56er',
        },
        offerer: expect.objectContaining({
          id: 'AGH',
          name: 'Gaumont cinéma',
          bic: 'bic',
          iban: 'iban',
          address: '256, rue des mimosas',
          siren: '256712456',
        }),
        offererId: 'AGH',
        venues: [],
      })
    })

    it('should return offerer id from url', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'TY56er',
            },
          ],
          userOfferers: [
            {
              id: 'AEKQ',
              modelName: 'UserOfferer',
              offererId: 'AGH',
              rights: 'admin',
              userId: 'TY56er',
            },
          ],
          offerers: [
            {
              id: 'AGH',
              name: 'Gaumont cinéma',
              bic: 'bic',
              iban: 'iban',
              siren: '256712456',
              address: '256, rue des mimosas',
            },
          ],
          venues: [],
        },
      }
      const ownProps = {
        match: {
          params: {
            offererId: 'AGH',
          },
        },
      }
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toMatchObject({
        offererId: 'AGH',
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('loadOffererById', () => {
      it('should load one offerer details', () => {
        // given
        const dispatch = jest.fn()
        const offererId = 'B44'

        // when
        mapDispatchToProps(dispatch).loadOffererById(offererId)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers/B44',
            method: 'GET',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          type: 'REQUEST_DATA_GET_/OFFERERS/B44',
        })
      })
    })
  })
})

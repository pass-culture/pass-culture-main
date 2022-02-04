import { mapStateToProps } from '../OffererDetailsContainer'

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
        offererId: 'AGH',
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
})

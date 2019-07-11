import { selectMediationsByOfferId } from '../selectMediationsByOfferId'

describe('selectMediationsByOfferId', () => {
  describe('when there is no mediations in state and no offerId provided', () => {
    it('should return an empty array', () => {
      // Given
      const state = {
        data: {
          mediations: [],
        },
      }

      // When
      const mediations = selectMediationsByOfferId(state)

      // Then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there is no mediations in state and offerId', () => {
    it('should return an empty array', () => {
      // Given
      const state = {
        data: {
          mediations: [],
        },
      }

      // When
      const mediations = selectMediationsByOfferId(state, 'MY')

      // Then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there are mediations in state and offerI is not matching', () => {
    it('should return an empty array', () => {
      // Given
      const state = {
        data: {
          mediations: [
            {
              id: 'HE',
              authorId: null,
              backText: 'Some back test',
              credit: null,
              dateCreated: '2019-03-29T09:41:49.119967Z',
              dateModifiedAtLastProvider: '2019-03-29T09:42:31.870558Z',
              frontText: 'Some front text',
              idAtProviders: null,
              isActive: false,
              lastProviderId: null,
              modelName: 'Mediation',
              offerId: 'NE',
              thumbCount: 1,
              tutoIndex: null,
            },
          ],
        },
      }

      // When
      const mediations = selectMediationsByOfferId(state, 'MY')

      // Then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there are mediations in state and offerId matching', () => {
    it('should return the mediations matching with offerId', () => {
      // Given
      const state = {
        data: {
          mediations: [
            {
              id: 'HE',
              authorId: null,
              backText: 'Some back test',
              credit: null,
              dateCreated: '2019-03-29T09:41:49.119967Z',
              dateModifiedAtLastProvider: '2019-03-29T09:42:31.870558Z',
              frontText: 'Some front text',
              idAtProviders: null,
              isActive: false,
              lastProviderId: null,
              modelName: 'Mediation',
              offerId: 'NE',
              thumbCount: 1,
              tutoIndex: null,
            },
          ],
        },
      }

      // When
      const mediations = selectMediationsByOfferId(state, 'NE')
      const expected = [
        {
          authorId: null,
          backText: 'Some back test',
          credit: null,
          dateCreated: '2019-03-29T09:41:49.119967Z',
          dateModifiedAtLastProvider: '2019-03-29T09:42:31.870558Z',
          frontText: 'Some front text',
          id: 'HE',
          idAtProviders: null,
          isActive: false,
          lastProviderId: null,
          modelName: 'Mediation',
          offerId: 'NE',
          thumbCount: 1,
          tutoIndex: null,
        },
      ]

      // Then
      expect(mediations).toStrictEqual(expected)
    })
  })
})

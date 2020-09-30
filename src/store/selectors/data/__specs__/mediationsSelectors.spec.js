import { selectMediationsByOfferId } from '../mediationsSelectors'

describe('selectMediationsByOfferId', () => {
  describe('when there is no mediations in state and no offerId provided', () => {
    it('should return an empty array', () => {
      // given
      const state = {
        data: {
          mediations: [],
        },
      }

      // when
      const mediations = selectMediationsByOfferId(state)

      // then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there is no mediations in state and offerId', () => {
    it('should return an empty array', () => {
      // given
      const state = {
        data: {
          mediations: [],
        },
      }

      // when
      const mediations = selectMediationsByOfferId(state, 'MY')

      // then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there are mediations in state and offerI is not matching', () => {
    it('should return an empty array', () => {
      // given
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

      // when
      const mediations = selectMediationsByOfferId(state, 'MY')

      // then
      expect(mediations).toStrictEqual([])
    })
  })

  describe('when there are mediations in state and offerId matching', () => {
    it('should return the mediations matching with offerId', () => {
      // given
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

      // when
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

      // then
      expect(mediations).toStrictEqual(expected)
    })
  })
})

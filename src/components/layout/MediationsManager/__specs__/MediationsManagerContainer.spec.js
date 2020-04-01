import state from '../../../utils/mocks/state'
import { mapStateToProps } from '../MediationsManagerContainer'

describe('src | components | pages | Offer | MediationsManager | MediationsMananagerContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {
        match: {
          params: {
            offerId: 'UU',
          },
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        hasMediations: true,
        atLeastOneActiveMediation: true,
        mediations: [
          {
            authorId: null,
            backText: 'Some back test',
            credit: null,
            dateCreated: '2019-03-07T10:39:23.560464Z',
            dateModifiedAtLastProvider: '2019-03-07T10:40:08.324689Z',
            frontText: 'Some front text',
            id: 'H4',
            idAtProviders: null,
            isActive: true,
            lastProviderId: null,
            modelName: 'Mediation',
            offerId: 'UU',
            thumbCount: 1,
            tutoIndex: null,
          },
        ],
        notification: null,
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-03-07T10:39:23.560392Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
          id: 'UU',
          idAtProviders: null,
          isActive: true,
          isEvent: false,
          isThing: true,
          lastProviderId: null,
          mediationsIds: ['H4'],
          modelName: 'Offer',
          productId: 'LY',
          stocksIds: ['MU'],
          venueId: 'DA',
        },
      })
    })
  })
})

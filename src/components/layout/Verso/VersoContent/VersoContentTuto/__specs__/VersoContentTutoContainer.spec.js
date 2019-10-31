import { mapStateToProps } from '../VersoContentTutoContainer'

describe('src | components | verso | verso-content | VersoContentTutoContainer', () => {
  describe('mapStateToProps', () => {
    it('maps imageURL with thumbURL from mediation', () => {
      // given
      const state = {
        data: {
          mediations: [
            {
              id: 'AQ',
              thumbUrl: 'http://fake_thumb.url/AQ',
            },
          ],
          bookings: [],
          offers: [],
        },
      }
      const ownProps = {
        match: {
          params: {
            mediationId: 'AQ',
          },
        },
      }

      // when then
      expect(mapStateToProps(state, ownProps).imageURL).toBe('http://fake_thumb.url/AQ_1')
    })
  })
})

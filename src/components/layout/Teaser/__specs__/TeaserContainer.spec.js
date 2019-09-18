import { mapStateToProps, mergeProps } from '../TeaserContainer'

describe('src | components | layout | Teaser | TeaserContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return default props', () => {
      // given
      const ownProps = {
        item: {
          offerId: 'o1',
          thumbUrl: 'fake/thumb/url',
        },
        handleToggleTeaser: jest.fn(),
        isEditMode: false,
      }
      const offer = {
        dateRange: ['2030-07-21T20:00:00Z', '2030-08-21T20:00:00Z'],
        id: 'o1',
        isActive: true,
        isFinished: false,
        isFullyBooked: false,
        name: 'Fake offer name',
        offerType: {
          appLabel: 'Fake offer type',
        },
        venue: {
          latitude: 48.91683,
          longitude: 2.4388,
        },
      }
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              isCancelled: false,
              stockId: 's1',
            },
          ],
          offers: [offer],
          stocks: [
            {
              id: 's1',
              beginningDatetime: '2030-08-21T20:00:00Z',
              offerId: 'o1',
            },
          ],
        },
        geolocation: {
          latitude: 48.8636537,
          longitude: 2.3371206000000004,
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        date: 'du 2030-7-21 au 2030-8-21',
        detailsUrl: '//details/o1',
        handleToggleTeaser: expect.any(Function),
        humanizeRelativeDistance: '10 km',
        isEditMode: false,
        name: 'Fake offer name',
        offerId: 'o1',
        offerTypeLabel: 'Fake offer type',
        statuses: [{ class: 'booked', label: 'Réservé' }],
        thumbUrl: 'fake/thumb/url',
      })
    })
  })

  describe('mergeProps', () => {
    it('should map trackConsultOffer using trackEvent from props', () => {
      const stateProps = {
        offerId: 'B4',
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      mergeProps(stateProps, {}, ownProps).trackConsultOffer()
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'consultOffer',
        name: 'B4',
      })
    })

    it('should spread props from stateProps', () => {
      const stateProps = {
        offerId: 'B4',
      }
      const result = mergeProps(stateProps, {}, {})
      expect(result.offerId).toBe('B4')
    })
  })
})

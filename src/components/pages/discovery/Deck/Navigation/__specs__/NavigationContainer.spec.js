import { mapDispatchToProps, mapStateToProps, mergeProps } from '../NavigationContainer'

describe('src | components | pages | discovery | Deck | Navigation | NavigationContainer', () => {
  describe('mapStateToProps', () => {
    it('should map backgroundGradient', () => {
      // given
      const state = {
        data: {
          recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
          offers: [{ id: 'AE' }],
          stocks: [{ offerId: 'AE' }],
        },
        geolocation: {
          latitude: '',
          longitude: '',
        },
      }
      const ownProps = {
        match: {
          params: {
            mediationId: 'FG',
            offerId: 'AE',
          },
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result.backgroundGradient).toBe(
        'linear-gradient(to bottom, rgba(0,0,0,0) 0%,black 30%,black 100%)'
      )
    })

    describe('when mapping distanceClue', () => {
      describe('when venue is virtual', () => {
        it('should return "offre en ligne"', () => {
          // given
          const state = {
            data: {
              recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
              offers: [
                {
                  id: 'AE',
                  venue: {
                    isVirtual: true,
                  },
                },
              ],
              stocks: [{ offerId: 'AE' }],
            },
            geolocation: {
              latitude: '',
              longitude: '',
            },
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'FG',
                offerId: 'AE',
              },
            },
          }

          // when
          const result = mapStateToProps(state, ownProps)

          // then
          expect(result.distanceClue).toBe('offre en ligne')
        })
      })

      describe('when venue is not virtual', () => {
        it('should return the humanized relative distance', () => {
          // given
          const state = {
            data: {
              recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
              offers: [
                {
                  id: 'AE',
                  venue: {
                    isVirtual: false,
                    latitude: 1,
                    longitude: 2,
                  },
                },
              ],
              stocks: [{ offerId: 'AE' }],
            },
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'FG',
                offerId: 'AE',
              },
            },
          }

          // when
          const result = mapStateToProps(state, ownProps)

          // then
          expect(result.distanceClue).toBe('0 m')
        })
      })
    })

    it('should map headerColor', () => {
      // given
      const state = {
        data: {
          recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
          offers: [{ id: 'AE' }],
          stocks: [{ offerId: 'AE' }],
        },
        geolocation: {
          latitude: '',
          longitude: '',
        },
      }
      const ownProps = {
        match: {
          params: {
            mediationId: 'FG',
            offerId: 'AE',
          },
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result.headerColor).toBe('black')
    })

    it('should map priceRange', () => {
      // given
      const state = {
        data: {
          recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
          offers: [{ id: 'AE' }],
          stocks: [
            { offerId: 'AE', price: 1, isBookable: true, available: 1 },
            { offerId: 'AE', price: 4, isBookable: true, available: 1 },
          ],
        },
        geolocation: {
          latitude: '',
          longitude: '',
        },
      }
      const ownProps = {
        match: {
          params: {
            mediationId: 'FG',
            offerId: 'AE',
          },
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result.priceRange).toStrictEqual([1, 4])
    })

    describe('when mapping separatior', () => {
      describe('when offer exists', () => {
        it('should return "\u00B7"', () => {
          // given
          const state = {
            data: {
              recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
              offers: [{ id: 'AE' }],
              stocks: [
                { offerId: 'AE', price: 1, isBookable: true, available: 1 },
                { offerId: 'AE', price: 4, isBookable: true, available: 1 },
              ],
            },
            geolocation: {
              latitude: '',
              longitude: '',
            },
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'FG',
                offerId: 'AE',
              },
            },
          }

          // when
          const result = mapStateToProps(state, ownProps)

          // then
          expect(result.separator).toBe('\u00B7')
        })
      })

      describe('when offer does not exists', () => {
        it('should an empty string with a space', () => {
          // given
          const state = {
            data: {
              recommendations: [{ offerId: 'AE', mediationId: 'FG' }],
              offers: [],
              stocks: [
                { offerId: 'AE', price: 1, isBookable: true, available: 1 },
                { offerId: 'AE', price: 4, isBookable: true, available: 1 },
              ],
            },
            geolocation: {
              latitude: '',
              longitude: '',
            },
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'FG',
                offerId: 'AE',
              },
            },
          }

          // when
          const result = mapStateToProps(state, ownProps)

          // then
          expect(result.separator).toBe(' ')
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('when mapping trackConsultOffer', () => {
      it('should dispatch a tracker Event with correct arguments', () => {
        // given
        const ownProps = {
          tracking: {
            trackEvent: jest.fn(),
          },
        }
        // when
        mapDispatchToProps(undefined, ownProps).trackConsultOffer('B4')

        // then
        expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
          action: 'consultOffer',
          name: 'B4',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread all stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {
        favorite: { offerId: 'B4' },
      }
      const dispatchProps = {
        trackConsultOffer: () => {},
      }
      const ownProps = {
        match: {
          params: {
            offerId: 'B4',
          },
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        favorite: { offerId: 'B4' },
        trackConsultOffer: expect.any(Function),
        match: {
          params: {
            offerId: 'B4',
          },
        },
      })
    })

    it('should wrap trackConsultOffer with offerId from stateProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        trackConsultOffer: jest.fn(),
      }
      const ownProps = {
        match: {
          params: {
            offerId: 'B4',
          },
        },
      }

      // when
      mergeProps(stateProps, dispatchProps, ownProps).trackConsultOffer()

      // then
      expect(dispatchProps.trackConsultOffer).toHaveBeenCalledWith('B4')
    })
  })
})

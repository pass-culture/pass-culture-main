/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
*/

import * as pcapi from 'repository/pcapi/pcapi'

import { mapDispatchToProps, mergeProps } from '../DeskContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  getBooking: jest.fn().mockImplementation(() => Promise.resolve()),
  validateBooking: jest.fn(),
  invalidateBooking: jest.fn(),
}))

describe('src | DeskContainer', () => {
  it('should retrieve a booking with a token given', () => {
    // given
    const { getBooking } = mapDispatchToProps(jest.fn())

    // when
    getBooking('ABCDEF')

    // then
    expect(pcapi.getBooking).toHaveBeenCalledWith('ABCDEF')
  })

  it('should valid a booking with a token given', () => {
    // given
    const { validateBooking } = mapDispatchToProps(jest.fn())

    // when
    validateBooking('ABCDEF')

    // then
    expect(pcapi.validateBooking).toHaveBeenCalledWith('ABCDEF')
  })

  it('should invalid a booking with a token given', () => {
    // given
    const { invalidateBooking } = mapDispatchToProps(jest.fn())

    // when
    invalidateBooking('ABCDEF')

    // then
    expect(pcapi.invalidateBooking).toHaveBeenCalledWith('ABCDEF')
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        getBooking: () => {},
      }
      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        getBooking: expect.any(Function),
        trackValidateBookingSuccess: expect.any(Function),
      })
    })

    it('should map a tracking event for validate a booking', () => {
      // given
      const stateProps = {
        offer: {
          id: 'B4',
        },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackValidateBookingSuccess('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'validateBooking',
        name: 'RTgfd67',
      })
    })
  })
})

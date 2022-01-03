/*
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 */

import * as pcapi from 'repository/pcapi/pcapi'

import { mapDispatchToProps } from '../DeskContainer'

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
})

import React from 'react'
import { shallow } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
import User from '../../ValueObjects/User'
import DepositVersion1 from '../DepositVersion1'
import DepositVersion2 from '../DepositVersion2'

describe('remainingCredit', () => {
  let props

  describe('when no deposit', () => {
    beforeEach(() => {
      props = {
        user: new User({
          expenses: [],
          wallet_balance: 0,
        }),
      }
    })

    it('should use DepositV2', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const isDepositV1Displayed = wrapper.find(DepositVersion1).exists()
      expect(isDepositV1Displayed).toBe(false)

      const isDepositV2Displayed = wrapper.find(DepositVersion2).exists()
      expect(isDepositV2Displayed).toBe(true)
    })
  })

  describe('when the deposit is version 1', () => {
    beforeEach(() => {
      props = {
        user: new User({
          deposit_version: 1,
          expenses: [
            { domain: 'all', current: 10, limit: 500 },
            { domain: 'digital', current: 20, limit: 201 },
            { domain: 'physical', current: 30, limit: 202 },
          ],
          wallet_balance: 351,
        }),
      }
    })

    it('should use DepositV1', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const isDepositV1Displayed = wrapper.find(DepositVersion1).exists()
      expect(isDepositV1Displayed).toBe(true)

      const isDepositV2Displayed = wrapper.find(DepositVersion2).exists()
      expect(isDepositV2Displayed).toBe(false)
    })
  })

  describe('when the deposit is version 2', () => {
    beforeEach(() => {
      props = {
        user: new User({
          deposit_version: 2,
          expenses: [
            { domain: 'all', current: 9, limit: 300 },
            { domain: 'digital', current: 20, limit: 100 },
          ],
          wallet_balance: 271,
        }),
      }
    })

    it('should use DepositV1', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const isDepositV1Displayed = wrapper.find(DepositVersion1).exists()
      expect(isDepositV1Displayed).toBe(false)

      const isDepositV2Displayed = wrapper.find(DepositVersion2).exists()
      expect(isDepositV2Displayed).toBe(true)
    })
  })
})

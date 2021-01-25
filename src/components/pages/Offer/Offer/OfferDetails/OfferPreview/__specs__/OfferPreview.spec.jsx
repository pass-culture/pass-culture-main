import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import * as pcapi from 'repository/pcapi/pcapi'

import OfferPreview from '../OfferPreview'

jest.mock('repository/pcapi/pcapi', () => ({
  getVenue: jest.fn(),
}))

const renderOfferPreview = async formValues => {
  await act(async () => {
    await render(<OfferPreview formValues={formValues} />)
  })
}

describe('offer preview', () => {
  beforeEach(() => {
    pcapi.getVenue.mockReturnValue(Promise.resolve())
  })

  describe('render', () => {
    it('should display title, description and withdrawal details when given', () => {
      // given
      const formValues = {
        name: 'Offer title',
        description: 'Offer description',
        withdrawalDetails: 'Offer withdrawal details',
      }

      // when
      renderOfferPreview(formValues)

      // then
      expect(screen.getByText('Offer title')).toBeInTheDocument()
      expect(screen.getByText('Offer description')).toBeInTheDocument()
      expect(screen.getByText('Modalités de retrait')).toBeInTheDocument()
      expect(screen.getByText('Offer withdrawal details')).toBeInTheDocument()
    })

    it('should truncate description text to maximum 300 characters', () => {
      // given
      const formValues = {
        description:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      }

      // when
      renderOfferPreview(formValues)

      // then
      const shrinkedDescriptionText = screen.getByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedDescriptionText).toBeInTheDocument()
    })

    it('should not display terms of withdrawal category if not given', () => {
      // given
      const formValues = {
        name: 'Offer title',
        description: 'Offer description',
        withdrawalDetails: '',
      }

      // when
      renderOfferPreview(formValues)

      // then
      expect(screen.queryByText('Modalités de retrait')).toBeNull()
    })

    it('should truncate withdrawal details text to maximum 300 characters', () => {
      // given
      const formValues = {
        withdrawalDetails:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      }

      // when
      renderOfferPreview(formValues)

      // then
      const shrinkedWithdrawalDetailsText = screen.getByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedWithdrawalDetailsText).toBeInTheDocument()
    })

    it('should display "isDuo", "Type" and "Price"', () => {
      // given
      const formValues = {
        isDuo: true,
      }

      // when
      renderOfferPreview(formValues)

      // then
      const typeText = screen.getByText('Type')
      expect(typeText).toBeInTheDocument()
      const duoText = screen.getByText('À deux !')
      expect(duoText).toBeInTheDocument()
      const priceText = screen.getByText('- - €')
      expect(priceText).toBeInTheDocument()
    })
  })
})

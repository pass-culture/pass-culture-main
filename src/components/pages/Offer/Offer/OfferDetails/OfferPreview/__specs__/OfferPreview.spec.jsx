import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import OfferPreview from '../OfferPreview'

const renderOffers = async formValues => {
  await act(async () => {
    await render(<OfferPreview formValues={formValues} />)
  })
}

describe('offer preview', () => {
  describe('render', () => {
    it('should display title, description and withdrawal details when given', async () => {
      // given
      const formValues = {
        name: 'Offer title',
        description: 'Offer description',
        withdrawalDetails: 'Offer withdrawal details',
      }

      // when
      await renderOffers(formValues)

      // then
      expect(await screen.queryByText('Offer title')).toBeInTheDocument()
      expect(await screen.queryByText('Offer description')).toBeInTheDocument()
      expect(await screen.queryByText('Modalités de retrait')).toBeInTheDocument()
      expect(await screen.queryByText('Offer withdrawal details')).toBeInTheDocument()
    })

    it('should truncate description text to maximum 300 characters', async () => {
      // given
      const formValues = {
        description:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      }

      // when
      await renderOffers(formValues)

      // then
      const shrinkedDescriptionText = await screen.queryByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedDescriptionText).toBeInTheDocument()
    })

    it('should not display terms of withdrawal category if not given', async () => {
      // given
      const formValues = {
        name: 'Offer title',
        description: 'Offer description',
        withdrawalDetails: '',
      }

      // when
      await renderOffers(formValues)

      // then
      expect(await screen.queryByText('Modalités de retrait')).not.toBeInTheDocument()
    })

    it('should truncate withdrawal details text to maximum 300 characters', async () => {
      // given
      const formValues = {
        withdrawalDetails:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      }

      // when
      await renderOffers(formValues)

      // then
      const shrinkedWithdrawalDetailsText = await screen.queryByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedWithdrawalDetailsText).toBeInTheDocument()
    })
  })
})

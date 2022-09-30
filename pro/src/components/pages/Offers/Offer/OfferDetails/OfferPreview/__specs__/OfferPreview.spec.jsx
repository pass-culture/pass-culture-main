import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { venueFactory } from 'utils/apiFactories'
import { loadFakeApiVenue } from 'utils/fakeApi'

import OfferPreview from '../OfferPreview'

const renderOfferPreview = async ({ props = {} }) => {
  render(<OfferPreview {...props} />)

  await waitFor(() => {
    expect(screen.getByTestId('offer-preview-section')).toBeInTheDocument()
  })
}

describe('offer preview', () => {
  describe('render', () => {
    it('should display title, description and withdrawal details when given', async () => {
      // given
      const props = {
        offerPreviewData: {
          name: 'Offer title',
          description: 'Offer description',
          withdrawalDetails: 'Offer withdrawal details',
        },
      }

      // when
      await renderOfferPreview({ props })

      // then
      expect(screen.getByText('Offer title')).toBeInTheDocument()
      expect(screen.getByText('Offer description')).toBeInTheDocument()
      expect(screen.getByText('Modalités de retrait')).toBeInTheDocument()
      expect(screen.getByText('Offer withdrawal details')).toBeInTheDocument()
    })

    it('should truncate description text to maximum 300 characters', async () => {
      // given
      const props = {
        offerPreviewData: {
          description:
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
        },
      }

      // when
      await renderOfferPreview({ props })

      // then
      const shrinkedDescriptionText = screen.getByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedDescriptionText).toBeInTheDocument()
    })

    it('should not display terms of withdrawal category if not given', async () => {
      // given
      const props = {
        offerPreviewData: {
          name: 'Offer title',
          description: 'Offer description',
          withdrawalDetails: '',
        },
      }

      // when
      await renderOfferPreview({ props })

      // then
      expect(screen.queryByText('Modalités de retrait')).toBeNull()
    })

    it('should truncate withdrawal details text to maximum 300 characters', async () => {
      // given
      const props = {
        offerPreviewData: {
          withdrawalDetails:
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
        },
      }

      // when
      await renderOfferPreview({ props })

      // then
      const shrinkedWithdrawalDetailsText = screen.getByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillu...'
      )
      expect(shrinkedWithdrawalDetailsText).toBeInTheDocument()
    })

    it('should display "isDuo", "Type" and "Price"', async () => {
      // given
      const props = {
        offerPreviewData: {
          isDuo: true,
        },
      }

      // when
      await renderOfferPreview({ props })

      // then
      const typeText = screen.getByText('Type')
      expect(typeText).toBeInTheDocument()
      const duoText = screen.getByText('À deux !')
      expect(duoText).toBeInTheDocument()
      const priceText = screen.getByText('- - €')
      expect(priceText).toBeInTheDocument()
    })

    describe('when venue is physical', () => {
      it('should display venue information if non virtual', async () => {
        //Given
        const venue = venueFactory()
        loadFakeApiVenue(venue)
        const props = {
          offerPreviewData: {
            venueId: venue.id,
          },
        }

        // When
        await renderOfferPreview({ props })

        // Then
        expect(
          screen.getByText('Mon Lieu - Ma Rue - 11100 - Ma Ville')
        ).toBeInTheDocument()
      })

      it('should not display any non given venue field', async () => {
        // Given
        const venue = venueFactory({
          address: null,
          postalCode: null,
        })
        loadFakeApiVenue(venue)
        const props = {
          offerPreviewData: {
            venueId: venue.id,
          },
        }

        // When
        await renderOfferPreview({ props })

        // Then
        expect(screen.getByText('Mon Lieu - Ma Ville')).toBeInTheDocument()
      })
    })

    describe('when venue is virtual', () => {
      it('should not display venue information if venue is virtual', async () => {
        // Given
        const venue = venueFactory({ isVirtual: true })
        loadFakeApiVenue(venue)
        const props = {
          offerPreviewData: {
            venueId: venue.id,
          },
        }

        // When
        await renderOfferPreview({ props })

        // Then
        expect(screen.queryByText('Où ?')).not.toBeInTheDocument()
      })
    })
  })
})

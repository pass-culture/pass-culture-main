import { api } from 'apiClient/api'
import { VenueTypeCode } from 'apiClient/v1'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import * as utils from 'commons/utils/savedPartnerPageVenueId'
import { SAVED_HOME_PAGE_VENUE_ID_KEYS } from 'commons/utils/savedPartnerPageVenueId'
import { beforeEach, expect } from 'vitest'

import { PartnerPages, PartnerPagesProps } from './PartnerPages'

const mockOfferer = defaultGetOffererResponseModel

const renderPartnerPages = (props: Partial<PartnerPagesProps> = {}) => {
  renderWithProviders(
    <PartnerPages
      venues={[defaultGetOffererVenueResponseModel]}
      offerer={mockOfferer}
      venueTypes={[{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }]}
      {...props}
    />
  )
}

describe('PartnerPages', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
      venueTypeCode: VenueTypeCode.FESTIVAL,
      bannerUrl: 'MyFirstImage',
      name: 'first venue',
      bannerMeta: {
        original_image_url: 'MyFirstImage',
        crop_params: {
          height_crop_percent: 12,
          width_crop_percent: 12,
          x_crop_percent: 12,
          y_crop_percent: 12,
        },
      },
    })
  })

  afterEach(() => {
    vi.spyOn(api, 'getVenue').mockReset()
    localStorage.clear()
  })

  describe('when the user has only one venue', () => {
    it('should not display select', async () => {
      renderPartnerPages({
        venues: [
          {
            ...defaultGetOffererVenueResponseModel,
            venueTypeCode: VenueTypeCode.FESTIVAL,
          },
        ],
      })

      expect(
        screen.getByRole('heading', { name: 'Votre page partenaire' })
      ).toBeInTheDocument()
      expect(
        screen.queryByLabelText(/Sélectionnez votre page partenaire/)
      ).not.toBeInTheDocument()

      await waitFor(() => {
        expect(screen.getByText('Festival')).toBeInTheDocument()
      })
      expect(
        screen.getByText('Gérer votre page pour le grand public')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Gérer votre page pour les enseignants')
      ).toBeInTheDocument()
    })
  })

  describe('when the user has multiple venues', () => {
    const mockedPartnerPageVenue = {
      ...defaultGetOffererVenueResponseModel,
      hasCreatedOffer: true,
      isPermanent: true,
      hasPartnerPage: true,
    }

    const mockedManagedVenuesLength = 10
    // We assume that there is a venue that has been filtered out
    // so we assign it an id of mockedManagedVenuesLength + 1.
    const mockedNotAPermanentPageVenueId = mockedManagedVenuesLength + 1
    const mockedManagedVenues = new Array(mockedManagedVenuesLength)
      .fill(mockedPartnerPageVenue)
      .map((_, index) => ({
        ...mockedPartnerPageVenue,
        id: index,
        publicName: `Venue ${index} - publicName`,
        name: `Venue ${index} - name`,
      }))

    it('should display a venues selection', async () => {
      renderPartnerPages({ venues: mockedManagedVenues })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: 'Vos pages partenaire' })
        ).toBeInTheDocument()
      })

      expect(
        screen.getByLabelText(/Sélectionnez votre page partenaire/)
      ).toBeInTheDocument()
    })

    it('should display & select previously selected / locally stored venue if available & relevant', async () => {
      // We assume that the last venue is the one that is stored.
      const locallyStoredVenueId = mockedManagedVenuesLength - 1

      localStorage.setItem(
        SAVED_HOME_PAGE_VENUE_ID_KEYS,
        JSON.stringify({
          [mockOfferer.id]: locallyStoredVenueId.toString(),
        })
      )

      renderPartnerPages({ venues: mockedManagedVenues })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: 'Vos pages partenaire' })
        ).toBeInTheDocument()
      })

      // getVenue is called with the locally stored venue id.
      expect(api.getVenue).toHaveBeenCalledWith(locallyStoredVenueId)
    })

    it('should display & select the 1st venue as default otherwise', async () => {
      // We assume that the locally stored venue is the venue that has no partner page,
      // to test a case where the stored venue was a partner page but is not anymore.
      const locallyStoredVenueId = mockedNotAPermanentPageVenueId

      localStorage.setItem(
        SAVED_HOME_PAGE_VENUE_ID_KEYS,
        JSON.stringify({
          [mockOfferer.id]: locallyStoredVenueId.toString(),
        })
      )

      renderPartnerPages({ venues: mockedManagedVenues })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: 'Vos pages partenaire' })
        ).toBeInTheDocument()
      })

      // getVenue is called with the first venue id.
      expect(api.getVenue).toHaveBeenCalledWith(
        mockedManagedVenues.find((v) => v.hasPartnerPage)?.id
      )
    })

    it('should save the venue id in local storage on selection', async () => {
      const setSavedPartnerPageVenueId = vi.fn()
      vi.spyOn(utils, 'setSavedPartnerPageVenueId').mockImplementation(() => ({
        setSavedPartnerPageVenueId,
      }))

      renderPartnerPages({ venues: mockedManagedVenues })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: 'Vos pages partenaire' })
        ).toBeInTheDocument()
      })

      const mockSelectedVenueId = Math.round(mockedManagedVenues.length / 2) + 1
      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire *'),
        mockSelectedVenueId.toString()
      )

      expect(utils.setSavedPartnerPageVenueId).toHaveBeenCalled()
      vi.spyOn(utils, 'setSavedPartnerPageVenueId').mockReset()
    })

    it('should should change image when changing venue', async () => {
      const venues = [
        {
          ...defaultGetOffererVenueResponseModel,
          id: 42,
          bannerUrl: 'MyFirstImage',
          name: 'first venue',
          bannerMeta: {
            original_image_url: 'MyFirstImage',
            crop_params: {
              height_crop_percent: 12,
              width_crop_percent: 12,
              x_crop_percent: 12,
              y_crop_percent: 12,
            },
          },
        },
        {
          ...defaultGetOffererVenueResponseModel,
          id: 666,
          bannerUrl: 'MyOtherImage',
          name: 'other venue',
          bannerMeta: {
            original_image_url: 'MyOtherImage',
            crop_params: {
              height_crop_percent: 12,
              width_crop_percent: 12,
              x_crop_percent: 12,
              y_crop_percent: 12,
            },
          },
        },
      ]

      renderPartnerPages({ venues })

      await waitFor(() => {
        expect(
          screen.getByAltText('Prévisualisation de l’image')
        ).toBeInTheDocument()
      })
      let image = screen.getByAltText('Prévisualisation de l’image')
      expect(image).toHaveAttribute('src', 'MyFirstImage')

      vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
        ...defaultGetVenue,
        id: 666,
        bannerUrl: 'MyOtherImage',
        name: 'other venue',
        bannerMeta: {
          original_image_url: 'MyOtherImage',
          crop_params: {
            height_crop_percent: 12,
            width_crop_percent: 12,
            x_crop_percent: 12,
            y_crop_percent: 12,
          },
        },
      })

      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire *'),
        '666'
      )

      await waitFor(() => {
        image = screen.getByAltText('Prévisualisation de l’image')
        expect(image).toHaveAttribute('src', 'MyOtherImage')
      })
    })
  })
})

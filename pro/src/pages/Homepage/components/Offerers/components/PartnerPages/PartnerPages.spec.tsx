import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, expect } from 'vitest'

import { api } from 'apiClient/api'
import { VenueTypeCode } from 'apiClient/v1'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { PartnerPagesProps, PartnerPages } from './PartnerPages'

const renderPartnerPages = (props: Partial<PartnerPagesProps> = {}) => {
  renderWithProviders(
    <PartnerPages
      venues={[defaultGetOffererVenueResponseModel]}
      offerer={defaultGetOffererResponseModel}
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

  it('should not display select if only one venue', async () => {
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

  it('should display select if multiple venues', async () => {
    renderPartnerPages({
      venues: [
        defaultGetOffererVenueResponseModel,
        {
          ...defaultGetOffererVenueResponseModel,
          id: 2,
          name: 'an other venue',
          publicName: 'a really cool name !',
        },
      ],
    })

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Vos pages partenaire' })
      ).toBeInTheDocument()
    })
    expect(
      screen.getByLabelText(/Sélectionnez votre page partenaire/)
    ).toBeInTheDocument()
    // it should use public name if available
    expect(screen.getByText('a really cool name !')).toBeInTheDocument()
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

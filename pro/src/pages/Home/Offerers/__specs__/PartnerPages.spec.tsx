import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { VenueTypeCode } from 'apiClient/v1'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  PartnerPages,
  PartnerPagesProps,
  SAVED_VENUE_ID_KEY,
} from '../PartnerPages'

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
  it('should not display select if only one venue', () => {
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

    expect(screen.getByText('Festival')).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour le grand public')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour les enseignants')
    ).toBeInTheDocument()
  })

  it('should display select if multiple venues', () => {
    renderPartnerPages({
      venues: [
        defaultGetOffererVenueResponseModel,
        {
          ...defaultGetOffererVenueResponseModel,
          id: 1,
          name: 'an other venue',
          publicName: 'a really cool name !',
        },
      ],
    })

    expect(
      screen.getByRole('heading', { name: 'Vos pages partenaire' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(/Sélectionnez votre page partenaire/)
    ).toBeInTheDocument()
    // it should use public name if available
    expect(screen.getByText('a really cool name !')).toBeInTheDocument()
  })

  it('should load saved venue in localStorage if no get parameter', () => {
    const selectedVenue = {
      ...defaultGetOffererVenueResponseModel,
      id: 666,
      name: 'super lieu',
    }
    localStorage.setItem(SAVED_VENUE_ID_KEY, selectedVenue.id.toString())

    renderPartnerPages({
      venues: [{ ...defaultGetOffererVenueResponseModel }, selectedVenue],
    })

    expect(screen.getAllByText('super lieu')[0]).toBeInTheDocument()
  })

  it('should not used saved venue in localStorage if it is not an option', () => {
    localStorage.setItem(SAVED_VENUE_ID_KEY, '123456')

    renderPartnerPages({ venues: [{ ...defaultGetOffererVenueResponseModel }] })

    expect(
      screen.getByText(defaultGetOffererVenueResponseModel.name)
    ).toBeInTheDocument()
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

    let image = screen.getByAltText('Prévisualisation de l’image')
    expect(image).toHaveAttribute('src', 'MyFirstImage')

    await userEvent.selectOptions(
      screen.getByLabelText('Sélectionnez votre page partenaire *'),
      '666'
    )

    image = screen.getByAltText('Prévisualisation de l’image')
    expect(image).toHaveAttribute('src', 'MyOtherImage')
  })
})

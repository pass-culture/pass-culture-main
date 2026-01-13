import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import {
  makeGetVenueManagingOffererResponseModel,
  makeGetVenueResponseModel,
} from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Offerers, type OfferersProps } from './Offerers'

const renderOfferers = (
  props: OfferersProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<Offerers {...props} />, options)
}

describe('<Offerers />', () => {
  const propsBase = {
    offererOptions: [{ label: 'name', value: '1' }],
    selectedOfferer: {
      ...defaultGetOffererResponseModel,
      id: 1,
    },
  } satisfies OfferersProps

  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 2,
        managingOffererId: 1,
        name: 'Venue A1',
      })
    )
  })

  it('should display soft-deleted warning when selected offerer is inactive', () => {
    renderOfferers(propsBase)

    expect(
      screen.getByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).toBeInTheDocument()
  })

  it('should display partner pages section when there is at least one permanent venue', async () => {
    const props = {
      ...propsBase,
      selectedOfferer: {
        ...propsBase.selectedOfferer,
        isActive: true,
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            isPermanent: true,
            isVirtual: false,
          },
        ],
      },
    }

    renderOfferers(props)

    expect(
      await screen.findByRole('heading', { name: /Votre page partenaire/i })
    ).toBeInTheDocument()
  })

  it('should display venue list when selected offerer is active', () => {
    const props = {
      ...propsBase,
      selectedOfferer: {
        ...defaultGetOffererResponseModel,
        isActive: true,
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            isVirtual: false,
            isPermanent: false,
            name: 'My venue',
            publicName: 'My venue',
          },
        ],
      },
    }

    renderOfferers(props)

    expect(
      screen.getByRole('link', { name: 'Gérer la page de My venue' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).not.toBeInTheDocument()
  })

  it('should display offerer creation links when user has no offerers', () => {
    const props = {
      ...propsBase,
      offererOptions: [],
      selectedOfferer: null,
    }

    renderOfferers(props)

    expect(
      screen.getByRole('heading', { name: 'Structures' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).not.toBeInTheDocument()
  })

  it('should render nothing specific when user has offerers but no selected offerer', () => {
    const props = {
      ...propsBase,
      selectedOfferer: null,
    }

    renderOfferers(props)

    expect(
      screen.queryByRole('heading', { name: /Votre page partenaire/i })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Structures' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).not.toBeInTheDocument()
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    const options: RenderWithProvidersOptions = {
      features: ['WIP_SWITCH_VENUE'],
    }

    it('should render the partner page for the selected venue', () => {
      const managingOfferer = makeGetVenueManagingOffererResponseModel({
        id: 7,
      })
      const selectedVenue = makeGetVenueResponseModel({
        id: 42,
        managingOfferer,
        name: 'My venue',
      })

      const props = {
        ...propsBase,
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          id: managingOfferer.id,
          isActive: true,
        },
      }

      renderOfferers(props, {
        ...options,
        storeOverrides: {
          user: { selectedVenue },
        },
      })

      expect(
        screen.getByRole('link', { name: 'Paramètres généraux' })
      ).toHaveAttribute(
        'href',
        `/structures/${managingOfferer.id}/lieux/${selectedVenue.id}/parametres`
      )

      expect(
        screen.queryByRole('link', { name: 'Gérer la page de My venue' })
      ).not.toBeInTheDocument()
    })

    it('should display individual section when venue has a partner page', () => {
      const managingOfferer = makeGetVenueManagingOffererResponseModel({
        id: 5,
      })
      const selectedVenue = makeGetVenueResponseModel({
        id: 99,
        managingOfferer,
        name: 'Partner Venue',
        hasPartnerPage: true,
      })

      const props = {
        ...propsBase,
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          id: managingOfferer.id,
          isActive: true,
        },
      }

      renderOfferers(props, {
        ...options,
        storeOverrides: {
          user: { selectedVenue },
        },
      })

      expect(
        screen.getByRole('link', {
          name: 'Gérer la page Partner Venue',
        })
      ).toBeInTheDocument()
    })

    it('should not render the partner page when no selected venue is set', () => {
      const props = {
        ...propsBase,
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          id: 1,
          isActive: true,
        },
      }

      renderOfferers(props, {
        ...options,
        storeOverrides: {
          user: { selectedVenue: null },
        },
      })

      expect(
        screen.queryByRole('link', { name: 'Paramètres généraux' })
      ).not.toBeInTheDocument()
    })
  })
})

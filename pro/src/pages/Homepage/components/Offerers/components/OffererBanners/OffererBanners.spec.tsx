import { screen } from '@testing-library/react'
import { describe } from 'vitest'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OffererBannersProps, OffererBanners } from './OffererBanners'

const mockNavigate = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: () => mockNavigate,
}))

const renderOffererBanners = (
  props: Partial<OffererBannersProps> = {},
  options: RenderWithProvidersOptions = {}
) => {
  renderWithProviders(
    <OffererBanners
      isUserOffererValidated={props.isUserOffererValidated ?? true}
      offerer={defaultGetOffererResponseModel}
      {...props}
    />,
    options
  )
}

describe('OffererBanners', () => {
  it('should not warn user when offerer is validated', () => {
    renderOffererBanners()

    expect(
      screen.queryByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).not.toBeInTheDocument()
  })

  it('should warn user that offerer is being validated when offerer is not yet validated', () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      isValidated: false,
    }
    renderOffererBanners({ offerer })

    expect(
      screen.getByText(
        'Votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })

  it('should warn user offerer is being validated when user attachment to offerer is not yet validated', () => {
    renderOffererBanners({ isUserOffererValidated: false })

    expect(
      screen.getByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })

  describe('WIP_ENABLE_OFFER_ADDRESS', () => {
    describe('user offerer not validated', () => {
      it('Should display the right wording with the FF enabled', () => {
        const offerer = {
          ...defaultGetOffererResponseModel,
          isValidated: false,
        }
        renderOffererBanners(
          { offerer, isUserOffererValidated: false },
          { features: ['WIP_ENABLE_OFFER_ADDRESS'] }
        )

        expect(
          screen.getByText(
            'Votre rattachement est en cours de traitement par les équipes du pass Culture'
          )
        ).toBeInTheDocument()
      })

      it('Should display the right wording without the FF enabled', () => {
        const offerer = {
          ...defaultGetOffererResponseModel,
          isValidated: false,
        }
        renderOffererBanners({ offerer, isUserOffererValidated: false })

        expect(
          screen.getByText(
            'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
          )
        ).toBeInTheDocument()
      })
    })

    it('Should display the right wording with the FF enabled', () => {
      const offerer = {
        ...defaultGetOffererResponseModel,
        managedVenues: [defaultGetOffererVenueResponseModel],
        isValidated: false,
      }
      renderOffererBanners(
        { offerer },
        { features: ['WIP_ENABLE_OFFER_ADDRESS'] }
      )

      expect(
        screen.getByText(
          /Vos offres seront publiées sous réserve de validation de votre structure./
        )
      ).toBeInTheDocument()
    })

    it('Should display the right wording without the FF enabled', () => {
      const offerer = {
        ...defaultGetOffererResponseModel,
        managedVenues: [defaultGetOffererVenueResponseModel],
        isValidated: false,
      }
      renderOffererBanners({ offerer })

      expect(
        screen.getByText(
          /Toutes les offres créées à l’échelle de vos lieux seront publiées sous réserve de validation de votre structure./
        )
      ).toBeInTheDocument()
    })
  })
})

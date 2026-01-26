import { screen } from '@testing-library/react'
import { describe } from 'vitest'

import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { OffererBanners, type OffererBannersProps } from './OffererBanners'

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
    <OffererBanners offerer={defaultGetOffererResponseModel} {...props} />,
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
    ).toBeFalsy()
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
})

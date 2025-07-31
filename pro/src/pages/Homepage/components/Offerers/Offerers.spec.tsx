import { screen } from '@testing-library/react'

import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { Offerers, OfferersProps } from './Offerers'

const renderOfferers = (
  props: Partial<OfferersProps> = {},
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <Offerers
      offererOptions={[{ label: 'name', value: '1' }]}
      selectedOfferer={defaultGetOffererResponseModel}
      isLoading={false}
      isUserOffererValidated
      venueTypes={[]}
      {...props}
    />,
    options
  )
}

describe('Offerers', () => {
  it('should display venue soft deleted', () => {
    renderOfferers()

    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).toBeInTheDocument()
  })
})

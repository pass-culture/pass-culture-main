import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { CollectiveDataForm } from '../CollectiveDataForm/CollectiveDataForm'

function renderCollectiveDataForm(options?: RenderWithProvidersOptions) {
  return renderWithProviders(
    <CollectiveDataForm
      statuses={[
        {
          value: 1,
          label: 'statut 1',
        },
        {
          value: 2,
          label: 'statut 2',
        },
      ]}
      domains={[
        { id: '1', label: 'domain 1' },
        { id: '2', label: 'domain 2' },
      ]}
      venue={defaultGetVenue}
    />,
    options
  )
}

describe('CollectiveDataForm', () => {
  it('should show all student levels when WIP_ENABLE_MARSEILLE is on', async () => {
    const featureOverrides = {
      features: ['WIP_ENABLE_MARSEILLE'],
    }
    renderCollectiveDataForm(featureOverrides)
    await userEvent.click(screen.getByLabelText('Public cible'))
    expect(
      screen.getByRole('checkbox', { name: 'Écoles Marseille - Maternelle' })
    ).toBeInTheDocument()
  })

  it('should show student levels without Marseille options when WIP_ENABLE_MARSEILLE is off', async () => {
    renderCollectiveDataForm()
    await userEvent.click(screen.getByLabelText('Public cible'))
    expect(
      screen.queryByText('Écoles Marseille - Maternelle')
    ).not.toBeInTheDocument()
  })
})
describe('OA feature flag', () => {
  it('should display the right wording without the OA FF', () => {
    renderCollectiveDataForm()
    expect(screen.getByText('Informations du lieu')).toBeInTheDocument()
  })
  it('should display the right wording with the OA FF', () => {
    renderCollectiveDataForm({
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    expect(screen.getByText('Informations de la structure')).toBeInTheDocument()
  })
})

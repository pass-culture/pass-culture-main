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
  it('should show all student levels when ENABLE_MARSEILLE is on', async () => {
    const featureOverrides = {
      features: ['ENABLE_MARSEILLE'],
    }
    renderCollectiveDataForm(featureOverrides)
    await userEvent.click(screen.getByLabelText('Public cible'))
    expect(
      screen.getByRole('checkbox', { name: 'Écoles Marseille - Maternelle' })
    ).toBeInTheDocument()
  })

  it('should show student levels without Marseille options when ENABLE_MARSEILLE is off', async () => {
    renderCollectiveDataForm()
    await userEvent.click(screen.getByLabelText('Public cible'))
    expect(
      screen.queryByText('Écoles Marseille - Maternelle')
    ).not.toBeInTheDocument()
  })
})

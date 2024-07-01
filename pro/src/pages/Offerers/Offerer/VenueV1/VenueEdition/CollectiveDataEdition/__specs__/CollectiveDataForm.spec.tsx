import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { CollectiveDataForm } from '../CollectiveDataForm/CollectiveDataForm'

describe('CollectiveDataForm', () => {
  it('should show all student levels when WIP_ENABLE_MARSEILLE is on', async () => {
    const featureOverrides = {
      features: ['WIP_ENABLE_MARSEILLE'],
    }
    renderCollectiveDataForm(featureOverrides)
    await userEvent.click(
      screen.getByPlaceholderText('Sélectionner un public cible')
    )
    expect(
      screen.getByRole('option', { name: 'Écoles Marseille - Maternelle' })
    ).toBeInTheDocument()
  })

  it('should show student levels without Marseille options when WIP_ENABLE_MARSEILLE is off', async () => {
    renderCollectiveDataForm()
    await userEvent.click(
      screen.getByPlaceholderText('Sélectionner un public cible')
    )
    expect(
      screen.queryByText('Écoles Marseille - Maternelle')
    ).not.toBeInTheDocument()
  })
})

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
        { value: 1, label: 'domain 1' },
        { value: 2, label: 'domain 2' },
      ]}
      culturalPartners={[
        {
          value: 'culturalPartner',
          label: 'Dans mon lieu',
        },
      ]}
      venue={defaultGetVenue}
    />,
    options
  )
}

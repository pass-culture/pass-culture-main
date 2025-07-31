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
          value: '1',
          label: 'statut 1',
        },
        {
          value: '2',
          label: 'statut 2',
        },
      ]}
      domains={[
        { id: '1', label: 'Arts numériques' },
        { id: '2', label: 'Architecture' },
      ]}
      venue={defaultGetVenue}
    />,
    options
  )
}

describe('CollectiveDataForm', () => {
  it('should check collective student', async () => {
    renderCollectiveDataForm()

    await userEvent.click(screen.getByLabelText('Public cible'))

    const studentCheckbox = screen.getByRole('checkbox', {
      name: 'Collège - 5e',
    })

    await userEvent.click(studentCheckbox)

    expect(studentCheckbox).toBeChecked()
  })

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

  it('should check collective domains', async () => {
    renderCollectiveDataForm()

    await userEvent.click(screen.getByLabelText('Domaines artistiques'))

    const domainsCheckbox = screen.getByRole('checkbox', {
      name: 'Architecture',
    })

    await userEvent.click(domainsCheckbox)

    expect(domainsCheckbox).toBeChecked()
  })
})

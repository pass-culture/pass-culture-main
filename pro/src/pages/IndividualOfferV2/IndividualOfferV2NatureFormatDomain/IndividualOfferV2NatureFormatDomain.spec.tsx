import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { FormatEnum, NatureEnum } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferV2NatureFormatDomain } from './IndividualOfferV2NatureFormatDomain'

const natures = [
  {
    formats: [
      { format: FormatEnum.LIVRE_PAPIER, label: 'Livre papier' },
      { format: FormatEnum.CD_VINYLE, label: 'CD ou vinyle' },
    ],
    label: 'Bien culturel',
    name: NatureEnum.BIEN,
  },
  {
    formats: [{ format: FormatEnum.DVD_BLU_RAY, label: 'DVD ou Blu-ray' }],
    label: 'Événement',
    name: NatureEnum.EVENEMENT,
  },
]

describe('<IndividualOfferV2NatureFormatDomain />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getNatureFormatDomain').mockResolvedValue(natures)
  })

  it('should have no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <IndividualOfferV2NatureFormatDomain />
    )
    await screen.findByRole('heading', { name: 'Nature et format' })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a loading indicator while nature and format data is loading', () => {
    vi.spyOn(api, 'getNatureFormatDomain').mockImplementation(
      () => new Promise(() => {})
    )

    renderWithProviders(<IndividualOfferV2NatureFormatDomain />)

    expect(screen.getByRole('status')).toHaveTextContent('Chargement en cours')
  })

  it('should display formats for the selected nature', async () => {
    const user = userEvent.setup()

    renderWithProviders(<IndividualOfferV2NatureFormatDomain />)

    expect(
      await screen.findByRole('group', { name: 'Sélectionnez la nature' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('group', { name: 'Sélectionnez le format' })
    ).not.toBeInTheDocument()

    await user.click(screen.getByRole('radio', { name: 'Bien culturel' }))

    expect(
      screen.getByRole('group', { name: 'Sélectionnez le format' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'Livre papier' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'CD ou vinyle' })
    ).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'Livre papier' }))
    expect(screen.getByRole('radio', { name: 'Livre papier' })).toBeChecked()

    await user.click(screen.getByRole('radio', { name: 'Événement' }))

    expect(
      screen.getByRole('radio', { name: 'DVD ou Blu-ray' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('radio', { name: 'Livre papier' })
    ).not.toBeInTheDocument()
  })

  it('should navigate to the home page when cancelling', async () => {
    const user = userEvent.setup()
    const { router } = renderWithProviders(
      <IndividualOfferV2NatureFormatDomain />
    )

    await user.click(
      await screen.findByRole('button', { name: 'Annuler et quitter' })
    )

    expect(router.state.location.pathname).toBe('/')
  })

  it('should navigate to the description step when submitting', async () => {
    const user = userEvent.setup()
    const { router } = renderWithProviders(
      <IndividualOfferV2NatureFormatDomain />
    )

    await user.click(
      await screen.findByRole('button', { name: 'Étape suivante' })
    )

    expect(router.state.location.pathname).toBe(
      '/offre/individuelle/v2/creation/description'
    )
  })
})

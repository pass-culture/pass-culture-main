import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { FormatEnum, NatureEnum } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferV2 } from '../IndividualOfferV2'
import { Component as IndividualOfferV2NatureFormatDomain } from './IndividualOfferV2NatureFormatDomain'

const natures = [
  {
    formats: [
      { format: FormatEnum.LIVRE_PAPIER, label: 'Livre papier' },
      { format: FormatEnum.CD, label: 'CD' },
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

const renderIndividualOfferV2NatureFormatDomain = () =>
  renderWithProviders(null, {
    initialRouterEntries: [
      '/offre/individuelle/v2/creation/nature-format-domaine',
    ],
    routes: [
      { path: '/accueil', element: <h2>Accueil</h2> },
      {
        path: '/offre/individuelle/v2/creation',
        element: <IndividualOfferV2 />,
        children: [
          {
            path: 'nature-format-domaine',
            element: <IndividualOfferV2NatureFormatDomain />,
          },
          { path: 'description', element: <h2>Description</h2> },
        ],
      },
    ],
  })

describe('<IndividualOfferV2NatureFormatDomain />', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.spyOn(api, 'getNatureFormatDomain').mockResolvedValue(natures)
  })

  it('should have no accessibility violations', async () => {
    const { container } = renderIndividualOfferV2NatureFormatDomain()
    await screen.findByRole('heading', { name: 'Nature et format' })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a loading indicator while nature and format data is loading', () => {
    vi.spyOn(api, 'getNatureFormatDomain').mockImplementation(
      () => new Promise(() => {})
    )

    renderIndividualOfferV2NatureFormatDomain()

    expect(screen.getByRole('status')).toHaveTextContent('Chargement en cours')
  })

  it('should display formats for the selected nature', async () => {
    const user = userEvent.setup()

    renderIndividualOfferV2NatureFormatDomain()

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
    expect(screen.getByRole('radio', { name: 'CD' })).toBeInTheDocument()
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
    const { router } = renderIndividualOfferV2NatureFormatDomain()

    await user.click(
      await screen.findByRole('link', { name: 'Annuler et quitter' })
    )

    expect(router.state.location.pathname).toBe('/accueil')
  })

  it('should navigate to the description step when submitting', async () => {
    const user = userEvent.setup()
    const { router } = renderIndividualOfferV2NatureFormatDomain()

    await user.click(
      await screen.findByRole('radio', { name: 'Bien culturel' })
    )
    await user.click(screen.getByRole('radio', { name: 'Livre papier' }))

    await user.click(screen.getByRole('button', { name: 'Étape suivante' }))

    expect(router.state.location.pathname).toBe(
      '/offre/individuelle/v2/creation/description'
    )
  })
})

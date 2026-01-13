import { render, screen } from '@testing-library/react'

import { NoResultsPage } from '../NoResultsPage'

describe('NoResultPage', () => {
  it('should display the searched query when something was searched ', () => {
    render(<NoResultsPage query="Musée du Louvre" venue={null} />)

    expect(screen.getByText('Musée du Louvre')).toBeInTheDocument()
  })

  it('should display the default message when nothing was searched ', () => {
    render(<NoResultsPage query="" venue={null} />)

    expect(
      screen.getByText(
        'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
      )
    ).toBeInTheDocument()
  })

  it('should display venue link when no result and venue filter active ', () => {
    const venue = {
      id: 1,
      name: 'Nom de la structire',
      publicName: 'Venue Public Name',
      relative: [],
      departementCode: '75',
      adageId: '123456',
    }

    render(<NoResultsPage query="noting nothing" venue={venue} />)

    expect(
      screen.getByRole('link', { name: /Voir la fiche du partenaire/ })
    ).toBeInTheDocument()
  })
})

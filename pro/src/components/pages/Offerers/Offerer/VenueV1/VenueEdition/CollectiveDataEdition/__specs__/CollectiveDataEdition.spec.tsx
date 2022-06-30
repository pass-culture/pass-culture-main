import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import CollectiveDataEdition from '../CollectiveDataEdition'
import React from 'react'
import userEvent from '@testing-library/user-event'

describe('CollectiveDataEdition', () => {
  it('should render form', () => {
    render(<CollectiveDataEdition />)

    const descriptionField = screen.queryByLabelText(
      'Ajoutez des informations complémentaires concernant l’EAC.',
      { exact: false }
    )
    const studentsField = screen.getByLabelText(/Public cible/)
    const websiteField = screen.getByLabelText(/URL de votre site web/)

    expect(descriptionField).toBeInTheDocument()
    expect(studentsField).toBeInTheDocument()
    expect(websiteField).toBeInTheDocument()
  })

  it('should display error fields', async () => {
    render(<CollectiveDataEdition />)

    const websiteField = screen.getByLabelText(/URL de votre site web/)
    const title = screen.getByText('Mes informations EAC')

    await userEvent.type(websiteField, 'wrong url')
    fireEvent.click(title)
    waitFor(() =>
      expect(
        screen.getByText('l’URL renseignée n’est pas valide')
      ).toBeInTheDocument()
    )
  })
})

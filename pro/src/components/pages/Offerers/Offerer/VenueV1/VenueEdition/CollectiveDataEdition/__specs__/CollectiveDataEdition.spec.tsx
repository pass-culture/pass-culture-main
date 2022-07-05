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
    const phoneField = screen.getByLabelText(/Téléphone/)
    const emailField = screen.getByLabelText(/E-mail/)

    expect(descriptionField).toBeInTheDocument()
    expect(studentsField).toBeInTheDocument()
    expect(websiteField).toBeInTheDocument()
    expect(phoneField).toBeInTheDocument()
    expect(emailField).toBeInTheDocument()
  })

  describe('error fields', () => {
    it('should display error fields', async () => {
      render(<CollectiveDataEdition />)

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Mes informations EAC')

      await userEvent.type(websiteField, 'wrong url')
      await userEvent.type(phoneField, 'not a valid phone')
      await userEvent.type(emailField, 'not a valid email')

      fireEvent.click(title)

      waitFor(() =>
        expect(
          screen.getByText('Votre email n’est pas valide')
        ).toBeInTheDocument()
      )
      expect(
        screen.getByText('Votre numéro de téléphone n’est pas valide')
      ).toBeInTheDocument()
      expect(
        screen.getByText('l’URL renseignée n’est pas valide')
      ).toBeInTheDocument()
    })

    it('should not display error fields when fields are valid', async () => {
      render(<CollectiveDataEdition />)

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Mes informations EAC')

      await userEvent.type(websiteField, 'https://mon-site.com')
      await userEvent.type(phoneField, '0600000000')
      await userEvent.type(emailField, 'email@domain.com')

      fireEvent.click(title)

      waitFor(() =>
        expect(
          screen.queryByText('Votre email n’est pas valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText('Votre numéro de téléphone n’est pas valide')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('l’URL renseignée n’est pas valide')
      ).not.toBeInTheDocument()
    })

    it('should not display error fields when fields are empty', async () => {
      render(<CollectiveDataEdition />)

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Mes informations EAC')

      fireEvent.click(websiteField)
      fireEvent.click(phoneField)
      fireEvent.click(emailField)
      fireEvent.click(title)

      waitFor(() =>
        expect(
          screen.queryByText('Votre email n’est pas valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText('Votre numéro de téléphone n’est pas valide')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('l’URL renseignée n’est pas valide')
      ).not.toBeInTheDocument()
    })
  })
})

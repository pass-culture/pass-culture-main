import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import CollectiveDataEdition from '../CollectiveDataEdition'
import { Provider } from 'react-redux'
import React from 'react'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

jest.mock('repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getVenuesEducationalStatuses: jest.fn(),
  },
}))

describe('CollectiveDataEdition', () => {
  beforeAll(() => {
    jest.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
      statuses: [
        {
          id: 1,
          name: 'statut 1',
        },
        {
          id: 2,
          name: 'statut 2',
        },
      ],
    })
    jest.spyOn(pcapi, 'getEducationalDomains').mockResolvedValue([
      { id: 1, name: 'domain 1' },
      { id: 2, name: 'domain 2' },
    ])
  })

  it('should render form', () => {
    render(
      <Provider store={configureTestStore({})}>
        <CollectiveDataEdition />
      </Provider>
    )

    const descriptionField = screen.queryByLabelText(
      'Ajoutez des informations complémentaires concernant l’EAC.',
      { exact: false }
    )
    const studentsField = screen.getByLabelText(/Public cible/)
    const websiteField = screen.getByLabelText(/URL de votre site web/)
    const phoneField = screen.getByLabelText(/Téléphone/)
    const emailField = screen.getByLabelText(/E-mail/)
    const domainsField = screen.getByLabelText(
      /Domaine artistique et culturel :/
    )
    const interventionAreaField = screen.getByLabelText(
      /Périmètre d’intervention :/
    )
    const statusField = screen.getByLabelText(/Statut :/)

    expect(descriptionField).toBeInTheDocument()
    expect(studentsField).toBeInTheDocument()
    expect(websiteField).toBeInTheDocument()
    expect(phoneField).toBeInTheDocument()
    expect(emailField).toBeInTheDocument()
    expect(domainsField).toBeInTheDocument()
    expect(interventionAreaField).toBeInTheDocument()
    expect(statusField).toBeInTheDocument()
  })

  describe('error fields', () => {
    it('should display error fields', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

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

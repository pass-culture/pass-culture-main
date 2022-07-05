import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import * as useNotification from 'components/hooks/useNotification'

import { domtomOptions, mainlandOptions } from '../interventionOptions'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import CollectiveDataEdition from '../CollectiveDataEdition'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
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

  describe('render', () => {
    it('should render form without errors', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const title = screen.getByText('Mes informations EAC')
      await waitFor(() => {
        expect(title).toBeInTheDocument()
      })

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

    it('should display toaster when some data could not be loaded', async () => {
      jest
        .spyOn(api, 'getVenuesEducationalStatuses')
        .mockRejectedValueOnce(
          new ApiError(
            {} as ApiRequestOptions,
            { status: 500 } as ApiResult,
            ''
          )
        )
      const notifyErrorMock = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        success: jest.fn,
        error: notifyErrorMock,
        information: jest.fn(),
        pending: jest.fn(),
        close: jest.fn(),
      }))

      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      await waitFor(() => {
        expect(notifyErrorMock).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
      })
    })
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

      await userEvent.click(title)

      expect(
        screen.queryByText('Votre numéro de téléphone n’est pas valide')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('l’URL renseignée n’est pas valide')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Votre email n’est pas valide')
      ).toBeInTheDocument()
    })

    it('should not display error fields when fields are valid', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Mes informations EAC')

      await userEvent.type(websiteField, 'https://mon-site.com')
      await userEvent.type(phoneField, '0600000000')
      await userEvent.type(emailField, 'email@domain.com')

      fireEvent.click(title)

      await waitFor(() =>
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
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Mes informations EAC')

      fireEvent.click(websiteField)
      fireEvent.click(phoneField)
      fireEvent.click(emailField)
      fireEvent.click(title)

      await waitFor(() =>
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

  describe('intervention area', () => {
    it('should select all departments when clicking on "Toute la France"', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const title = screen.getByText('Mes informations EAC')
      await waitFor(() => {
        expect(title).toBeInTheDocument()
      })

      const interventionAreaField = screen.getByLabelText(
        /Périmètre d’intervention :/
      )
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(
          screen.queryByText(/France métropolitaine et d’outre-mer/)
        ).toBeInTheDocument()
      )
      const allDepartmentsOption = screen.getByLabelText(
        /France métropolitaine et d’outre-mer/
      )
      await userEvent.click(allDepartmentsOption)
      ;[...mainlandOptions, ...domtomOptions].forEach(option => {
        expect(screen.getByLabelText(option.label)).toBeChecked()
      })
    })

    it('should select all mainland departments when clicking on "France métropolitaine"', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const interventionAreaField = screen.getByLabelText(
        /Périmètre d’intervention :/
      )
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(screen.queryByText('France métropolitaine')).toBeInTheDocument()
      )
      const mainlandOption = screen.getByLabelText('France métropolitaine')
      await userEvent.click(mainlandOption)
      ;[...mainlandOptions].forEach(option => {
        expect(screen.getByLabelText(option.label)).toBeChecked()
      })
    })

    it('should select only domtom options after selecting "Toute la France" then unselecting "France métropolitaine"', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const interventionAreaField = screen.getByLabelText(
        /Périmètre d’intervention :/
      )
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(screen.queryByText('France métropolitaine')).toBeInTheDocument()
      )

      await userEvent.click(
        screen.getByLabelText(/France métropolitaine et d’outre-mer/)
      )
      await userEvent.click(screen.getByLabelText('France métropolitaine'))
      expect(
        screen.queryByLabelText(mainlandOptions[0].label)
      ).not.toBeChecked()
      domtomOptions.forEach(option =>
        expect(screen.queryByLabelText(option.label)).toBeChecked()
      )
    })

    it('should select (unselect) "Toute la France" and "France métropolitaine" when selecting (unselecting) all (one) departments', async () => {
      render(
        <Provider store={configureTestStore({})}>
          <CollectiveDataEdition />
        </Provider>
      )

      const interventionAreaField = screen.getByLabelText(
        /Périmètre d’intervention :/
      )
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(screen.queryByText('France métropolitaine')).toBeInTheDocument()
      )

      // check all mainland options
      await Promise.all(
        mainlandOptions.map(option => {
          userEvent.click(screen.getByLabelText(option.label))
        })
      )
      await waitFor(() => {
        const mainlandOption = screen.getByLabelText('France métropolitaine')
        expect(mainlandOption).toBeChecked()
      })

      // check all other departments
      await Promise.all(
        domtomOptions.map(option => {
          userEvent.click(screen.getByLabelText(option.label))
        })
      )
      await waitFor(() => {
        const allFranceOption = screen.getByLabelText(
          /France métropolitaine et d’outre-mer/
        )
        expect(allFranceOption).toBeChecked()
      })

      // unselect dom tom department
      await userEvent.click(screen.getByLabelText(domtomOptions[0].label))
      await waitFor(() =>
        expect(
          screen.getByLabelText(/France métropolitaine et d’outre-mer/)
        ).not.toBeChecked()
      )

      await userEvent.click(screen.getByLabelText(mainlandOptions[0].label))
      await waitFor(() =>
        expect(screen.getByLabelText('France métropolitaine')).not.toBeChecked()
      )
    })
  })
})

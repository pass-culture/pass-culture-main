import { fireEvent, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import Notification from 'components/Notification/Notification'
import { renderWithProviders } from 'utils/renderWithProviders'

import ButtonDownloadCSV from '../ButtonDownloadCSV'

const fetchMock = createFetchMock(vi)

const renderButtonDownloadCSV = async ({ props, storeOverrides }) =>
  renderWithProviders(
    <>
      <ButtonDownloadCSV {...props}>Fake Button</ButtonDownloadCSV>
      <Notification />
    </>,
    { storeOverrides }
  )

describe('src | components | Layout | ButtonDownloadCSV', () => {
  describe('render', () => {
    it('should disable button during download', async () => {
      fetch.mockResponse(JSON.stringify({}), { status: 200 })

      const props = {
        filename: 'test-csv',
        href: 'https://test.com',
        mimeType: 'text/csv',
        isDisabled: false,
      }

      renderButtonDownloadCSV({ props })

      const button = await screen.findByText('Fake Button')
      expect(button).toBeEnabled()

      // RomainC: we need fireEvent here to test intermediate state of the componenent
      fireEvent.click(button)
      expect(button).toBeDisabled()

      await waitFor(() => {
        expect(button).toBeEnabled()
      })
    })

    it('should display notification if there is an error during download', async () => {
      fetchMock.mockResponse(JSON.stringify({}), { status: 500 })

      const props = {
        filename: 'test-csv',
        href: 'https://test.com',
        mimeType: 'text/csv',
        isDisabled: false,
      }

      renderButtonDownloadCSV({ props })

      const button = screen.getByText('Fake Button')

      await userEvent.click(button)

      expect(
        screen.getByText('Il y a une erreur avec le chargement du fichier csv.')
      ).toBeInTheDocument()
    })
  })
})

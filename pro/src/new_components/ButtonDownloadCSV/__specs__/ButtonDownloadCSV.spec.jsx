import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from '../../../store/testUtils'
import ButtonDownloadCSV from '../ButtonDownloadCSV'

const renderButtonDownloadCSV = async ({ props, storeOverrides }) => {
  const store = configureTestStore(storeOverrides)

  return render(
    <Provider store={store}>
      <ButtonDownloadCSV {...props}>Fake Title</ButtonDownloadCSV>
    </Provider>
  )
}
describe('src | components | Layout | ButtonDownloadCSV', () => {
  describe('render', () => {
    it('should disable button during download', async () => {
      // await new Promise(resolve => {
      fetch.mockResponse(JSON.stringify({}), { status: 200 })

      const props = {
        filename: 'test-csv',
        href: 'http://test.com',
        mimeType: 'text/csv',
        isDisabled: false,
      }

      renderButtonDownloadCSV({ props })

      const button = await screen.findByText('Fake Title')
      expect(button).toBeEnabled()

      // maybe we need fireEvent here
      fireEvent.click(button)
      expect(button).toBeDisabled()

      // then
      waitFor(() => {
        expect(button).toBeEnabled()
      })
    })
  })
})

import '@testing-library/jest-dom'

import { fireEvent, render, screen } from '@testing-library/react'
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
      await new Promise(resolve => {
        fetch.mockResponse(JSON.stringify({}), { status: 200 })

        const props = {
          filename: 'test-csv',
          href: 'http://test.com',
          mimeType: 'text/csv',
          isDisabled: false,
        }

        renderButtonDownloadCSV({ props })

        const button = screen.getByText('Fake Title')
        expect(button).toBeEnabled()
        fireEvent.click(button)
        expect(button).toBeDisabled()

        setTimeout(() => {
          // then
          expect(button).toBeEnabled()
          resolve()
        })
      })
    })
  })
})

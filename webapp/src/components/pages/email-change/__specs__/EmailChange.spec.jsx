import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import { toast } from 'react-toastify'
import EmailChange from '../EmailChange'
import {
  EMAIL_CHANGE_SUCCESS,
  EMAIl_CHANGE_FAILED,
  EMAIl_CHANGE_LINK_EXPIRED,
  REQUEST_EMAIL_CHANGE_PAGE_LINK,
  SIGNIN_PAGE_LINK,
} from '../EmailChange'

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

describe('email change page', () => {
  let props
  beforeEach(() => {
    jest.resetAllMocks()
    jest.spyOn(global.Date, 'now').mockImplementation(() => 848016000000)

    props = {
      history: {
        push: jest.fn(),
      },
      location: {
        search: '?token=toto&expiration_timestamp=848016000001',
      },
    }
  })

  describe('when arriving on the page', () => {
    it('should display success message and redirect when the data are ok', async () => {
      // Given
      global.fetch.mockResolvedValueOnce({ status: 204 })

      // When
      await mount(
        <MemoryRouter>
          <EmailChange {...props} />
        </MemoryRouter>
      )
      await global.fetch

      // Then
      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(global.fetch).toHaveBeenCalledWith('http://localhost/beneficiaries/change_email', {
        body: JSON.stringify({ token: 'toto' }),
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'PUT',
      })
      expect(toast.success).toHaveBeenCalledWith(EMAIL_CHANGE_SUCCESS)
      expect(props.history.push).toHaveBeenCalledWith(SIGNIN_PAGE_LINK)
    })

    it('should redirect and display toast error when the link is expired', async () => {
      // Given
      props.location.search = '?token=toto&expiration_timestamp=84801599'
      global.fetch.mockResolvedValueOnce({ status: 204 })

      // When
      await mount(
        <MemoryRouter>
          <EmailChange {...props} />
        </MemoryRouter>
      )
      await global.fetch

      // Then
      expect(global.fetch).toHaveBeenCalledTimes(0)
      expect(toast.error).toHaveBeenCalledWith(EMAIl_CHANGE_LINK_EXPIRED)
      expect(props.history.push).toHaveBeenCalledWith(REQUEST_EMAIL_CHANGE_PAGE_LINK)
    })

    it('should redirect and display toast error when the server responds error', async () => {
      // Given
      global.fetch.mockResolvedValueOnce({ status: 400 })

      // When
      await mount(
        <MemoryRouter>
          <EmailChange {...props} />
        </MemoryRouter>
      )
      await global.fetch

      // Then
      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(toast.error).toHaveBeenCalledWith(EMAIl_CHANGE_FAILED)
      expect(props.history.push).toHaveBeenCalledWith(REQUEST_EMAIL_CHANGE_PAGE_LINK)
    })

    it('should redirect and display toast error when the call crashes', async () => {
      // Given
      global.fetch.mockRejectedValueOnce('API is down')

      // When
      await mount(
        <MemoryRouter>
          <EmailChange {...props} />
        </MemoryRouter>
      )
      await global.fetch

      // Then
      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(toast.error).toHaveBeenCalledWith(EMAIl_CHANGE_FAILED)
      expect(props.history.push).toHaveBeenCalledWith(REQUEST_EMAIL_CHANGE_PAGE_LINK)
    })
  })
})

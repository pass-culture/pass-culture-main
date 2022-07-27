import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { useState } from 'react'
import { MemoryRouter } from 'react-router'

import { apiV2 } from 'api/api'
import { ApiError, HTTP_STATUS } from 'api/helpers'
import {
  BookingFormula,
  BookingOfferType,
  GetBookingResponse,
} from 'api/v2/gen'
import { IDeskProps, MESSAGE_VARIANT } from 'screens/Desk'
import { Button } from 'ui-kit'

import Desk from '../Desk'

const TestScreen = ({
  getBooking,
  submitInvalidate,
  submitValidate,
}: IDeskProps) => {
  const [response, setResponse] = useState({})
  return (
    <div>
      <h1>Test Screen loaded</h1>
      <Button onClick={async () => setResponse(await getBooking(testToken))}>
        getBooking
      </Button>
      <Button
        onClick={async () => setResponse(await submitInvalidate(testToken))}
      >
        submitInvalidate
      </Button>
      <Button
        onClick={async () => setResponse(await submitValidate(testToken))}
      >
        submitValidate
      </Button>
      <div data-testid="response-data">{JSON.stringify(response, null, 2)}</div>
    </div>
  )
}

jest.mock('screens/Desk/Desk', () => ({
  __esModule: true,
  ...jest.requireActual('screens/Desk/Desk'),
  default: TestScreen,
}))

const testToken = 'AAAAAA'

const renderDeskRoute = async () => {
  const rtlReturns = render(
    <MemoryRouter>
      <Desk />
    </MemoryRouter>
  )
  await screen.findByText('Test Screen loaded')
  return {
    ...rtlReturns,
    buttonGetBooking: screen.getByText('getBooking'),
    buttonSubmitInvalidate: screen.getByText('submitInvalidate'),
    buttonSubmitValidate: screen.getByText('submitValidate'),
    responseDataContainer: screen.getByTestId('response-data'),
  }
}

describe('src | routes | Desk', () => {
  it('test getBooking success', async () => {
    const apiBooking: GetBookingResponse = {
      bookingId: 'test_booking_id',
      dateOfBirth: '1980-02-01T20:00:00Z',
      email: 'test@email.com',
      formula: BookingFormula.PLACE,
      isUsed: false,
      offerId: 12345,
      offerType: BookingOfferType.EVENEMENT,
      phoneNumber: '0100000000',
      publicOfferId: 'test_public_offer_id',
      theater: 'theater_any',
      venueAddress: null,
      venueName: 'mon lieu',
      datetime: '2001-02-01T20:00:00Z',
      ean13: 'test ean113',
      offerName: 'Nom de la structure',
      price: 13,
      quantity: 1,
      userName: 'USER',
      venueDepartmentCode: '75',
    }
    const deskBooking = {
      datetime: '2001-02-01T20:00:00Z',
      ean13: 'test ean113',
      offerName: 'Nom de la structure',
      price: 13,
      quantity: 1,
      userName: 'USER',
      venueDepartmentCode: '75',
    }
    jest
      .spyOn(apiV2, 'getBookingsGetBookingByTokenV2')
      .mockResolvedValue(apiBooking)
    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiV2.getBookingsGetBookingByTokenV2).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.booking).toBeDefined()
    expect(response.booking.datetime).toBe(deskBooking.datetime)
    expect(response.booking.ean13).toBe(deskBooking.ean13)
    expect(response.booking.offerName).toBe(deskBooking.offerName)
    expect(response.booking.price).toBe(deskBooking.price)
    expect(response.booking.quantity).toBe(deskBooking.quantity)
    expect(response.booking.userName).toBe(deskBooking.userName)
    expect(response.booking.venueDepartmentCode).toBe(
      deskBooking.venueDepartmentCode
    )
  })

  it('test getBooking failure, booking already validated', async () => {
    const globalErrorMessage = 'Cette réservation a déjà été validée'
    jest.spyOn(apiV2, 'getBookingsGetBookingByTokenV2').mockRejectedValue(
      new ApiError(HTTP_STATUS.GONE, {
        global: [globalErrorMessage],
      })
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiV2.getBookingsGetBookingByTokenV2).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(response.error.isTokenValidated).toBe(true)
    expect(response.error.message).toBe(globalErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.DEFAULT)
  })

  it('test getBooking failure, booking canceled', async () => {
    const cancelledErrorMessage = 'Cette réservation a déjà été validée'
    jest.spyOn(apiV2, 'getBookingsGetBookingByTokenV2').mockRejectedValue(
      new ApiError(HTTP_STATUS.GONE, {
        booking_cancelled: [cancelledErrorMessage],
      })
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiV2.getBookingsGetBookingByTokenV2).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(response.error.isTokenValidated).toBe(false)
    expect(response.error.message).toBe(cancelledErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.ERROR)
  })

  it('test getBooking failure, api error', async () => {
    const globalErrorMessage = 'Server error'
    jest.spyOn(apiV2, 'getBookingsGetBookingByTokenV2').mockRejectedValue(
      new ApiError(HTTP_STATUS.NOT_FOUND, {
        global: [globalErrorMessage],
      })
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiV2.getBookingsGetBookingByTokenV2).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(response.error.isTokenValidated).toBe(false)
    expect(response.error.message).toBe(globalErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.ERROR)
  })

  it('test submitInvalidate success', async () => {
    jest
      .spyOn(apiV2, 'patchBookingsPatchBookingKeepByToken')
      .mockResolvedValue({})

    const { buttonSubmitInvalidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitInvalidate)
    await waitFor(() => {
      expect(apiV2.patchBookingsPatchBookingKeepByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')
    expect(Object.keys(response)).toHaveLength(0)
  })

  it('test submitInvalidate error', async () => {
    const submitInvalidateErrorMessage = 'An Error Happen on submitInvalidate !'
    jest.spyOn(apiV2, 'patchBookingsPatchBookingKeepByToken').mockRejectedValue(
      new ApiError(HTTP_STATUS.FORBIDDEN, {
        global: [submitInvalidateErrorMessage],
      })
    )

    const { buttonSubmitInvalidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitInvalidate)
    await waitFor(() => {
      expect(apiV2.patchBookingsPatchBookingKeepByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(Object.keys(response.error)).toHaveLength(2)
    expect(response.error.message).toBe(submitInvalidateErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.ERROR)
  })

  it('test submitValidate success', async () => {
    jest
      .spyOn(apiV2, 'patchBookingsPatchBookingUseByToken')
      .mockResolvedValue({})

    const { buttonSubmitValidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitValidate)
    await waitFor(() => {
      expect(apiV2.patchBookingsPatchBookingUseByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')
    expect(Object.keys(response)).toHaveLength(0)
  })

  it('test submitValidate error', async () => {
    const submitInvalidateErrorMessage = 'An Error Happen on submitValidate!'
    jest.spyOn(apiV2, 'patchBookingsPatchBookingUseByToken').mockRejectedValue(
      new ApiError(HTTP_STATUS.FORBIDDEN, {
        global: [submitInvalidateErrorMessage],
      })
    )

    const { buttonSubmitValidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitValidate)
    await waitFor(() => {
      expect(apiV2.patchBookingsPatchBookingUseByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(Object.keys(response.error)).toHaveLength(2)
    expect(response.error.message).toBe(submitInvalidateErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.ERROR)
  })
})

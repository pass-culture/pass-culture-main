import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { useState } from 'react'
import { MemoryRouter } from 'react-router'

import { apiContremarque } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import {
  ApiError,
  BookingFormula,
  BookingOfferType,
  GetBookingResponse,
} from 'apiClient/v2'
import { ApiRequestOptions } from 'apiClient/v2/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v2/core/ApiResult'
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
      .spyOn(apiContremarque, 'getBookingByTokenV2')
      .mockResolvedValue(apiBooking)
    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
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
    jest
      .spyOn(apiContremarque, 'getBookingByTokenV2')
      .mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { status: HTTP_STATUS.GONE, body: {} } as ApiResult,
          globalErrorMessage
        )
      )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
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

  it('test getBooking failure, booking cancelled', async () => {
    const cancelledErrorMessage = 'Cette réservation a été annulée'
    jest.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: HTTP_STATUS.GONE,
          body: { booking_cancelled: 'Cette réservation a été annulée' },
        } as ApiResult,
        cancelledErrorMessage
      )
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
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

  it('test getBooking failure, booking reimbursed', async () => {
    const cancelledErrorMessage = 'Cette réservation a été remboursée'
    jest.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: HTTP_STATUS.FORBIDDEN,
          body: { payment: 'Cette réservation a été remboursée' },
        } as ApiResult,
        cancelledErrorMessage
      )
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
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

  it('test getBooking failure, booking cant be validated yet', async () => {
    const notConfirmedErrorMessage =
      'Cette réservation a été effectuée le 05/09/2022.\nVeuillez attendre jusqu’au 07/09/2022 pour valider la contremarque.'
    jest.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: HTTP_STATUS.FORBIDDEN,
          body: {
            booking:
              'Cette réservation a été effectuée le 05/09/2022.\nVeuillez attendre jusqu’au 07/09/2022 pour valider la contremarque.',
          },
        } as ApiResult,
        notConfirmedErrorMessage
      )
    )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')

    expect(Object.keys(response)).toHaveLength(1)
    expect(response.error).toBeDefined()
    expect(response.error.isTokenValidated).toBe(false)
    expect(response.error.message).toBe(notConfirmedErrorMessage)
    expect(response.error.variant).toBe(MESSAGE_VARIANT.ERROR)
  })

  it('test getBooking failure, api error', async () => {
    const globalErrorMessage = 'Server error'
    jest
      .spyOn(apiContremarque, 'getBookingByTokenV2')
      .mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { status: HTTP_STATUS.NOT_FOUND } as ApiResult,
          globalErrorMessage
        )
      )

    const { buttonGetBooking, responseDataContainer } = await renderDeskRoute()

    userEvent.click(buttonGetBooking)
    await waitFor(() => {
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith(
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
    jest.spyOn(apiContremarque, 'patchBookingKeepByToken').mockResolvedValue()

    const { buttonSubmitInvalidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitInvalidate)
    await waitFor(() => {
      expect(apiContremarque.patchBookingKeepByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')
    expect(Object.keys(response)).toHaveLength(0)
  })

  it('test submitInvalidate error', async () => {
    const submitInvalidateErrorMessage = 'An Error Happen on submitInvalidate !'
    jest.spyOn(apiContremarque, 'patchBookingKeepByToken').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: HTTP_STATUS.FORBIDDEN,
          body: {
            global: submitInvalidateErrorMessage,
          },
        } as ApiResult,
        ''
      )
    )

    const { buttonSubmitInvalidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitInvalidate)
    await waitFor(() => {
      expect(apiContremarque.patchBookingKeepByToken).toHaveBeenCalledWith(
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
    jest.spyOn(apiContremarque, 'patchBookingUseByToken').mockResolvedValue()

    const { buttonSubmitValidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitValidate)
    await waitFor(() => {
      expect(apiContremarque.patchBookingUseByToken).toHaveBeenCalledWith(
        testToken
      )
    })
    // to fix - no-conditional-in-test
    const response = JSON.parse(responseDataContainer.textContent || '')
    expect(Object.keys(response)).toHaveLength(0)
  })

  it('test submitValidate error', async () => {
    const submitInvalidateErrorMessage = 'An Error Happen on submitValidate!'
    jest.spyOn(apiContremarque, 'patchBookingUseByToken').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: HTTP_STATUS.FORBIDDEN,
          body: {
            global: submitInvalidateErrorMessage,
          },
        } as ApiResult,
        ''
      )
    )

    const { buttonSubmitValidate, responseDataContainer } =
      await renderDeskRoute()

    userEvent.click(buttonSubmitValidate)
    await waitFor(() => {
      expect(apiContremarque.patchBookingUseByToken).toHaveBeenCalledWith(
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

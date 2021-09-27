import '@testing-library/jest-dom'
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from "history"
import React from "react"
import { Provider } from "react-redux"
import { Router } from "react-router-dom"

import { configureTestStore } from "../../../../../../../store/testUtils"
import VenueCreation from "../VenueCreation"

const initialize = ( { props }) => {
  const store = configureTestStore()
  const history = createBrowserHistory()
  history.push(`/structures/AE/lieux/TR?modification`)

  const utils = render(
    <Provider store={store}>
      <Router history={history}>
        <VenueCreation {...props} />
      </Router>
    </Provider>
  )
  return {
    ...utils
  }
}

describe('contact form enable in venue creation form', () => {

  let push
  let props

  beforeEach(() => {
    push = jest.fn()
    props = {
      formInitialValues: {
        id: 'CM',
      },
      history: {
        location: {
          pathname: '/fake',
        },
        push: push,
      },
      handleInitialRequest: jest.fn(),
      handleSubmitRequest: jest.fn(),
      handleSubmitRequestSuccess: jest.fn(),
      handleSubmitRequestFail: jest.fn(),
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      offerer: {
        id: 'BQ',
        name: 'Maison du chocolat',
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
      trackCreateVenue: jest.fn(),
      trackModifyVenue: jest.fn(),
      venueTypes: [],
      venueLabels: [],
    }
  })

  it('should display contact fields', async ()=> {
    initialize({ props })
    const contactPhoneNumber = await screen.findByLabelText("Téléphone")
    const contactMail = await screen.findByLabelText("Mail")
    const contactUrl = await screen.findByLabelText("URL de votre site web")

    expect(contactPhoneNumber).toBeInTheDocument()
    expect(contactMail).toBeInTheDocument()
    expect(contactUrl).toBeInTheDocument()

    expect(contactPhoneNumber).toBeEnabled()
    expect(contactMail).toBeEnabled()
    expect(contactUrl).toBeEnabled()

  })

  it('should fill contact fields', async ()=> {
    initialize({ props })
    const contactPhoneNumber = await screen.findByLabelText("Téléphone")
    const contactMail = await screen.findByLabelText("Mail")
    const contactUrl = await screen.findByLabelText("URL de votre site web")

    userEvent.type(contactPhoneNumber, '0606060606')
    userEvent.type(contactMail, 'test@test.com')
    userEvent.type(contactUrl, 'https://some-url-test.com')

    await waitFor(() => {
      expect(contactUrl).toHaveValue('https://some-url-test.com')
    })
    expect(contactPhoneNumber).toHaveValue('0606060606')
    expect(contactMail).toHaveValue('test@test.com')
  })



})

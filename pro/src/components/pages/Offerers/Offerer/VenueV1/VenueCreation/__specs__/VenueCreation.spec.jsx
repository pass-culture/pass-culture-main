import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import VenueCreationContainer from '../VenueCreationContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  getBusinessUnits: jest.fn().mockResolvedValue([]),
}))

const renderVenueCreation = ({ props, storeOverrides = {} }) => {
  const store = configureTestStore(storeOverrides)
  const history = createBrowserHistory()
  history.push(`/structures/AE/lieux/TR?modification`)

  return render(
    <Provider store={store}>
      <Router history={history}>
        <VenueCreationContainer {...props} />
      </Router>
    </Provider>
  )
}

describe('contact form enable in venue creation form', () => {
  let push
  let props
  let storeOverrides = {
    data: {
      users: [
        { publicName: 'René', isAdmin: false, email: 'rené@example.com' },
      ],
    },
  }

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
      venueTypes: [],
      venueLabels: [],
    }
  })

  it('should display contact fields', async () => {
    renderVenueCreation({ props, storeOverrides })
    const contactPhoneNumber = await screen.findByLabelText('Téléphone :')
    const contactMail = await screen.findByLabelText('Mail :')
    const contactUrl = await screen.findByLabelText('URL de votre site web :')

    expect(contactPhoneNumber).toBeInTheDocument()
    expect(contactMail).toBeInTheDocument()
    expect(contactUrl).toBeInTheDocument()

    expect(contactPhoneNumber).toBeEnabled()
    expect(contactMail).toBeEnabled()
    expect(contactUrl).toBeEnabled()
  })

  it('should fill contact fields', async () => {
    renderVenueCreation({ props, storeOverrides })
    const contactPhoneNumber = await screen.findByLabelText('Téléphone :')
    const contactMail = await screen.findByLabelText('Mail :')
    const contactUrl = await screen.findByLabelText('URL de votre site web :')

    userEvent.paste(contactPhoneNumber, '0606060606')
    userEvent.paste(contactMail, 'test@test.com')
    userEvent.paste(contactUrl, 'https://some-url-test.com')

    expect(contactUrl).toHaveValue('https://some-url-test.com')
    expect(contactPhoneNumber).toHaveValue('0606060606')
    expect(contactMail).toHaveValue('test@test.com')
  })

  describe('business unit fileds', () => {
    storeOverrides = {
      ...storeOverrides,
      features: {
        list: [
          {
            nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET',
            isActive: true,
          },
        ],
      },
    }
    beforeEach(() => {
      pcapi.getBusinessUnits.mockResolvedValue([
        {
          id: 20,
          iban: 'FR0000000000000002',
          name: 'Business unit #1',
          siret: '22222222311111',
        },
        {
          id: 21,
          iban: 'FR0000000000000003',
          name: 'Business unit #2',
          siret: '22222222311222',
        },
      ])
    })

    it('should display business unit select list when structure have business units', async () => {
      // Given
      renderVenueCreation({ props, storeOverrides })

      // Then
      await expect(
        screen.findByLabelText(
          'Coordonnées bancaires pour vos remboursements :'
        )
      ).resolves.toBeInTheDocument()
    })

    it('should not display business unit select list when structure does not have busiess units', async () => {
      // Given
      pcapi.getBusinessUnits.mockResolvedValue([])

      // When
      renderVenueCreation({ props, storeOverrides })

      // Then
      await expect(
        screen.queryByLabelText(
          'Coordonnées bancaires pour vos remboursements :'
        )
      ).not.toBeInTheDocument()
    })
  })
})

import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import ReimbursementPoint from '../ReimbursementPoint'

jest.mock('apiClient/api', () => ({
  api: {
    getAvailableReimbursementPoints: jest.fn(),
    getVenue: jest.fn(),
  },
}))
const renderReimbursementPoint = async (props, store) => {
  const rtlReturn = await render(
    <Provider store={store}>
      <MemoryRouter path={'/structures'}>
        <Form onSubmit={() => {}}>
          {() => <ReimbursementPoint {...props} />}
        </Form>
      </MemoryRouter>
    </Provider>
  )

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}
const mockLogEvent = jest.fn()

describe('src | Venue | ReimbursementPoint', () => {
  const history = createBrowserHistory()
  const initialVenue = {
    id: 'AA',
    nonHumanizedId: 1,
    name: 'fake venue name',
  }
  const offerer = {
    id: 'BB',
    nonHumanizedId: 2,
    name: 'fake offerer name',
  }
  let props
  let store
  beforeEach(() => {
    props = { initialVenue, offerer }
    store = configureTestStore({
      app: { logEvent: mockLogEvent },
    })
  })

  it('should display reimbursement point secion  when offerer has at least one', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([
      {
        venueName: 'Venue #1',
        siret: '111222333',
        venueId: 1,
        bic: 'BDFEFRPP',
        iban: 'FR9410010000000000000000022',
      },
    ])

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.queryByText('Sélectionner des coordonnées dans la liste')
    ).toBeInTheDocument()
  })

  it('should display reimbursement point with the correct name ', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([
      {
        venueName: 'Venue #1',
        siret: '111222333',
        venueId: 1,
        bic: 'BDFEFRPP',
        iban: 'FR9410010000000000000000022',
      },
    ])

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.queryByText('Venue #1 - FR9410010000000000000000022')
    ).toBeInTheDocument()
  })

  it('should not display reimbursement point selection  when offerer has not one', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.queryByText('Sélectionner des coordonnées dans la liste')
    ).not.toBeInTheDocument()
  })

  it('should display add cb button when venue does not have reimbursement point', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.getByRole('button', {
        name: 'Ajouter des coordonnées bancaires',
      })
    ).toBeInTheDocument()
  })
  it('should track button on click in modal', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])
    history.push('/structures')
    // When
    await renderReimbursementPoint(props, store)
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Ajouter des coordonnées bancaires',
      })
    )
    // Then
    await waitFor(() =>
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_ADD_BANK_INFORMATIONS,
        {
          from: '/structures',
        }
      )
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: /J'ai compris/,
      })
    )
    await waitFor(() =>
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        Events.CLICKED_NO_PRICING_POINT_SELECTED_YET,
        {
          from: '/structures',
        }
      )
    )
  })

  it('should display modify button when venue has already add dms cb', async () => {
    // Given
    const venueWithReimbursementPoint = {
      id: 'AA',
      nonHumanizedId: 1,
      reimbursementPointId: 1,
      name: 'fake venue name',
    }
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([
      {
        venueName: 'fake venue name',
        siret: '111222333',
        venueId: 1,
        bic: 'BDFEFRPP',
        iban: 'FR9410010000000000000000022',
      },
    ])
    props.initialVenue = venueWithReimbursementPoint

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.getByRole('button', {
        name: 'Modifier mes coordonnées bancaires',
      })
    ).toBeInTheDocument()
  })

  it('should display banner when venue has dms application pending', async () => {
    // Given
    const venueWithPendingApplication = {
      id: 'AA',
      name: 'fake venue name',
      hasPendingBankInformationApplication: true,
    }

    props.initialVenue = venueWithPendingApplication
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

    // When
    await renderReimbursementPoint(props, store)

    // Then
    expect(
      screen.queryByText(
        'Les coordonnées bancaires de votre lieu sont en cours de validation par notre service financier.'
      )
    ).toBeInTheDocument()
  })

  it('should reload component when closing dms pop-in', async () => {
    const venueWithSiret = {
      id: 'AA',
      name: 'fake venue name',
      siret: '11111111100000',
    }
    props.initialVenue = venueWithSiret

    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])
    jest.spyOn(api, 'getVenue').mockResolvedValue(props.initialVenue)

    // When
    await renderReimbursementPoint(props, store)

    const addReimbursementPointButton = screen.getByRole('button', {
      name: 'Ajouter des coordonnées bancaires',
    })
    await userEvent.click(addReimbursementPointButton)

    // Then
    expect(
      screen.queryByText(
        'Avant d’ajouter des nouvelles coordonnées bancaires via la plateforme Démarches Simplifiées :'
      )
    ).toBeInTheDocument()
    const closeModalButton = screen.getByTitle('Fermer la modale')
    await userEvent.click(closeModalButton)

    expect(api.getVenue).toHaveBeenCalledTimes(1)
  })
})

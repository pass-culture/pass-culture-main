import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'

import { Form } from 'react-final-form'

import React from 'react'
import ReimbursementPoint from '../ReimbursementPoint'
import { api } from 'apiClient/api'
import userEvent from '@testing-library/user-event'

jest.mock('apiClient/api', () => ({
  api: {
    getAvailableReimbursementPoints: jest.fn(),
    getVenue: jest.fn(),
  },
}))

const renderReimbursementPoint = async props => {
  const rtlReturn = await render(
    <Form onSubmit={() => {}}>{() => <ReimbursementPoint {...props} />}</Form>
  )

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}

describe('src | Venue | ReimbursementPoint', () => {
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
  beforeEach(() => {
    props = { initialVenue, offerer }
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
    await renderReimbursementPoint(props)

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
    await renderReimbursementPoint(props)

    // Then
    expect(
      screen.queryByText('Venue #1 - FR9410010000000000000000022')
    ).toBeInTheDocument()
  })

  it('should not display reimbursement point selection  when offerer has not one', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

    // When
    await renderReimbursementPoint(props)

    // Then
    expect(
      screen.queryByText('Sélectionner des coordonnées dans la liste')
    ).not.toBeInTheDocument()
  })

  it('should display add cb button when venue does not have reimbursement point', async () => {
    // Given
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

    // When
    await renderReimbursementPoint(props)

    // Then
    expect(
      screen.getByRole('button', {
        name: 'Ajouter des coordonnées bancaires',
      })
    ).toBeInTheDocument()
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
    await renderReimbursementPoint(props)

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
    await renderReimbursementPoint(props)

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
    await renderReimbursementPoint(props)

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

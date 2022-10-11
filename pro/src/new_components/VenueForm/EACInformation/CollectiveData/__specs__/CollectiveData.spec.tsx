import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import { IVenue } from 'core/Venue'
import { configureTestStore } from 'store/testUtils'

import CollectiveData from '../CollectiveData'

describe('CollectiveData', () => {
  const venue = {
    collectiveDescription: 'une description',
    collectiveDomains: [1, 2],
    collectiveEmail: 'mon@email.com',
    collectiveInterventionArea: null,
    collectiveLegalStatus: 2,
    collectiveNetwork: ['1'],
    collectivePhone: '',
    collectiveStudents: ['Collège - 3e'],
    collectiveWebsite: undefined,
  } as unknown as IVenue // we only test for used fields

  beforeEach(() => {
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })
  })

  const store = configureTestStore({})

  it('should display title if the value is available', async () => {
    const venue = {
      collectiveDescription: 'une description',
      collectiveDomains: [1, 2],
      collectiveEmail: 'mon@email.com',
      collectiveInterventionArea: ['area 1'],
      collectiveLegalStatus: 2,
      collectiveNetwork: ['1'],
      collectivePhone: '0600000000',
      collectiveStudents: ['Collège - 3e'],
      collectiveWebsite: 'www.google.fr',
    } as unknown as IVenue // we only test for used fields

    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })

    render(
      <Provider store={store}>
        <CollectiveData venue={venue} />
      </Provider>
    )

    expect(
      await screen.findByText(/Domaines artistiques et culturels/)
    ).toBeInTheDocument()
    expect(
      await screen.findByText(/Présentation de vos informations EAC/)
    ).toBeInTheDocument()
    expect(await screen.findByText(/Public cible/)).toBeInTheDocument()
    expect(await screen.findByText(/Statut/)).toBeInTheDocument()
    expect(await screen.findByText(/E-mail/)).toBeInTheDocument()
    expect(await screen.findByText(/Téléphone :/)).toBeInTheDocument()
    expect(
      await screen.findByText(/URL de votre site web :/)
    ).toBeInTheDocument()
    expect(await screen.findByText(/Zone de mobilité :/)).toBeInTheDocument()
  })

  it('should not display title if value is empty', async () => {
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })

    render(
      <Provider store={store}>
        <CollectiveData venue={venue} />
      </Provider>
    )

    expect(screen.queryByText(/Téléphone :/)).not.toBeInTheDocument()
    expect(
      screen.queryByText(/URL de votre site web :/)
    ).not.toBeInTheDocument()
    expect(screen.queryByText(/Zone de mobilité :/)).not.toBeInTheDocument()
  })

  it('should display the networks available from the api call', async () => {
    jest.spyOn(api, 'getEducationalPartners').mockResolvedValue({
      partners: [
        { id: 1, libelle: 'Libellé 1' },
        { id: 2, libelle: 'Libellé 2' },
      ],
    })

    render(
      <Provider store={store}>
        <CollectiveData venue={venue} />
      </Provider>
    )

    expect(await screen.findByText('Libellé 1')).toBeInTheDocument()
    expect(await screen.queryByText('Libellé 2')).not.toBeInTheDocument()
  })
})

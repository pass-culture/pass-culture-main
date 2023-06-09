import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { IVenue } from 'core/Venue'
import { renderWithProviders } from 'utils/renderWithProviders'

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

    renderWithProviders(<CollectiveData venue={venue} />)

    expect(
      await screen.findByText(/Domaines artistiques et culturels/)
    ).toBeInTheDocument()
    expect(
      await screen.findByText(/Présentation de vos informations EAC/)
    ).toBeInTheDocument()
    expect(await screen.findByText(/Public cible/)).toBeInTheDocument()
    expect(await screen.findByText(/Statut/)).toBeInTheDocument()
    expect(await screen.findByText(/Email/)).toBeInTheDocument()
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

    renderWithProviders(<CollectiveData venue={venue} />)

    expect(screen.queryByText(/Téléphone :/)).not.toBeInTheDocument()
    expect(
      screen.queryByText(/URL de votre site web :/)
    ).not.toBeInTheDocument()
    expect(screen.queryByText(/Zone de mobilité :/)).not.toBeInTheDocument()
  })

  it('should display the networks available when available', async () => {
    jest.spyOn(api, 'getEducationalPartners').mockResolvedValue({
      partners: [
        { id: 1, libelle: 'Libellé 1' },
        { id: 2, libelle: 'Libellé 2' },
      ],
    })

    renderWithProviders(<CollectiveData venue={venue} />)

    expect(await screen.findByText('Libellé 1')).toBeInTheDocument()
    expect(await screen.queryByText('Libellé 2')).not.toBeInTheDocument()
  })
})

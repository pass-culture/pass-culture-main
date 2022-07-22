import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import EACInformation from '../EACInformation'
import { GetVenueResponseModel } from 'apiClient/v1'
import type { History } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'
import { api } from 'apiClient/api'
import { createBrowserHistory } from 'history'

jest.mock('apiClient/api', () => ({
  api: {
    getEducationalPartners: jest.fn(),
  },
}))

describe('EACInformation', () => {
  let history: History

  beforeAll(() => {
    history = createBrowserHistory()
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })
  })

  describe('on venue creation', () => {
    it('should display information banner when user is creating venue and can create collective offers', async () => {
      render(
        <Router history={history}>
          <EACInformation venue={null} isCreatingVenue offererId="O1" />
        </Router>
      )

      expect(
        await screen.findByText(
          'Une fois votre lieu créé, vous pourrez renseigner des informations pour les enseignants en revenant sur cette page.'
        )
      ).toBeInTheDocument()
      expect(
        await screen.findByRole('link', { name: 'Renseigner mes informations' })
      ).toHaveAttribute('aria-disabled')
    })
  })

  describe('on venue edition', () => {
    it('when venue has collective data', async () => {
      const venue = {
        id: 'V1',
        collectiveDescription: 'une description',
        collectiveDomains: [1, 2],
        collectiveEmail: 'mon@email.com',
        collectiveInterventionArea: null,
        collectiveLegalStatus: 2,
        collectiveNetwork: [],
        collectivePhone: '',
        collectiveStudents: ['Collège - 3e'],
        collectiveWebsite: undefined,
      } as unknown as GetVenueResponseModel // we only test for used fields

      render(
        <Router history={history}>
          <EACInformation venue={venue} offererId="O1" />
        </Router>
      )

      expect(await screen.findByText(/E-mail/)).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: 'Modifier mes informations' })
      ).toBeInTheDocument()
    })

    it('when venue has no collective data', async () => {
      const venue = {
        id: 'V1',
        collectiveDescription: '',
        collectiveDomains: [],
        collectiveEmail: '',
        collectiveInterventionArea: null,
        collectiveLegalStatus: null,
        collectiveNetwork: [],
        collectivePhone: '',
        collectiveStudents: [],
        collectiveWebsite: undefined,
      } as unknown as GetVenueResponseModel // we only test for used fields
      render(
        <Router history={history}>
          <EACInformation venue={venue} offererId="O1" />
        </Router>
      )

      expect(screen.queryByText(/E-mail/)).not.toBeInTheDocument()
      const link = screen.getByRole('link', {
        name: 'Renseigner mes informations',
      })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', `/structures/O1/lieux/V1/eac`)
    })
  })
})

import '@testing-library/jest-dom'
import { act, fireEvent, render, screen, within } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Homepage from '../Homepage'

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
}))

const renderHomePage = async () => {
  const store = configureTestStore({
    data: {
      users: [
        {
          id: 'fake_id',
          firstName: 'John',
          lastName: 'Do',
          email: 'john.do@dummy.xyz',
          phoneNumber: '01 00 00 00 00',
        },
      ],
    },
  })
  return await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <Homepage />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('homepage : Tabs : Offerers', () => {
  let baseOfferers
  let baseVenues

  beforeEach(() => {
    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        city: 'Cayenne',
        name: 'Bar des amis',
        id: 'GE',
        postalCode: '97300',
        siren: '111111111',
      },
      {
        address: 'RUE DE NIEUPORT',
        city: 'Drancy',
        id: 'FQ',
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
      },
    ]
    baseVenues = [
      {
        id: 'test_venue_id_1',
        isVirtual: true,
        managingOffererId: baseOfferers[0].id,
        name: 'Le Sous-sol (Offre numérique)',
        offererName: 'Bar des amis',
        publicName: null,
      },
      {
        id: 'test_venue_id_2',
        isVirtual: false,
        managingOffererId: baseOfferers[0].id,
        name: 'Le Sous-sol (Offre physique)',
        offererName: 'Bar des amis',
        publicName: null,
      },
    ]

    pcapi.getOfferers.mockResolvedValue(baseOfferers)
    pcapi.getVenuesForOfferer.mockResolvedValue(baseVenues)
  })

  afterEach(() => {
    pcapi.getOfferers.mockClear()
    pcapi.getVenuesForOfferer.mockClear()
  })

  describe('render', () => {
    beforeEach(async () => {
      await renderHomePage()
    })

    it('should display section and subsection titles', async () => {
      expect(await screen.findByText('Informations pratiques')).toBeInTheDocument()
      expect(await screen.findByText('Coordonnées bancaires')).toBeInTheDocument()
      expect(await screen.findByText('Profil et aide', { selector: 'h2' })).toBeInTheDocument()
      expect(await screen.findByText('Profil')).toBeInTheDocument()
      expect(await screen.findByText('Aide et support')).toBeInTheDocument()
      expect(await screen.findByText('Modalités d’usage', { selector: 'h2' })).toBeInTheDocument()
    })

    it('should display help links', async () => {
      const contactLink = await screen.findByText('Contacter le support', { selector: 'a' })
      const cguLink = await screen.findByText('Conditions Générales d’Utilisation', {
        selector: 'a',
      })
      const faqLink = await screen.findByText('Foire Aux Questions', { selector: 'a' })

      expect(contactLink).toBeInTheDocument()
      expect(cguLink).toBeInTheDocument()
      expect(faqLink).toBeInTheDocument()

      expect(contactLink.getAttribute('href')).toBe('mailto:support@passculture.app')
      expect(cguLink.getAttribute('href')).toBe('https://pass.culture.fr/cgu-professionnels/')
      expect(faqLink.getAttribute('href')).toBe(
        'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
      )
    })

    it('should display offerer select', () => {
      const selectedOffer = baseOfferers[0]
      expect(screen.getByDisplayValue(selectedOffer.name)).toBeInTheDocument()
    })

    it('should display first offerer informations', async () => {
      const selectedOfferer = baseOfferers[0]
      const selectedOffererAddress = `${selectedOfferer.address} ${selectedOfferer.postalCode} ${selectedOfferer.city}`
      expect(await screen.findByText(selectedOfferer.siren)).toBeInTheDocument()
      expect(await screen.findByText(selectedOfferer.name, { selector: 'dd' })).toBeInTheDocument()
      expect(await screen.findByText(selectedOffererAddress)).toBeInTheDocument()
    })

    it('should display offerer venues informations', async () => {
      const virtualVenueTitle = await screen.findByText('Lieu numérique')
      expect(virtualVenueTitle).toBeInTheDocument()

      const offlineVenueTitle = await screen.findByText(baseVenues[1].name)
      expect(offlineVenueTitle).toBeInTheDocument()
      const offlineVenueContainer = offlineVenueTitle.closest('div')
      expect(
        within(offlineVenueContainer).getByText('Modifier', { exact: false })
      ).toBeInTheDocument()
    })

    describe('when selected offerer change', () => {
      let newSelectedOfferer
      let newSelectedOffererVenues
      beforeEach(async () => {
        const selectedOffer = baseOfferers[0]
        newSelectedOfferer = baseOfferers[1]
        newSelectedOffererVenues = [
          {
            id: 'test_venue_id_3',
            isVirtual: true,
            managingOffererId: newSelectedOfferer.id,
            name: 'New venue (Offre numérique)',
            offererName: newSelectedOfferer.name,
            publicName: null,
          },
          {
            id: 'test_venue_id_4',
            isVirtual: false,
            managingOffererId: newSelectedOfferer.id,
            name: 'New venue (Offre physique)',
            offererName: newSelectedOfferer.name,
            publicName: null,
          },
        ]
        pcapi.getVenuesForOfferer.mockResolvedValue(newSelectedOffererVenues)

        await act(async () => {
          await fireEvent.change(screen.getByDisplayValue(selectedOffer.name), {
            target: { value: newSelectedOfferer.id },
          })
        })
      })

      it('should change displayed offerer informations', async () => {
        const selectedOffererAddress = `${newSelectedOfferer.address} ${newSelectedOfferer.postalCode} ${newSelectedOfferer.city}`

        expect(await screen.findByText(newSelectedOfferer.siren)).toBeInTheDocument()
        expect(
          await screen.findByText(newSelectedOfferer.name, { selector: 'dd' })
        ).toBeInTheDocument()
        expect(await screen.findByText(selectedOffererAddress)).toBeInTheDocument()
      })

      it('should display new offerer venues informations', async () => {
        const virtualVenueTitle = await screen.findByText('Lieu numérique')
        expect(virtualVenueTitle).toBeInTheDocument()

        const offlineVenueTitle = await screen.findByText(newSelectedOffererVenues[1].name)
        expect(offlineVenueTitle).toBeInTheDocument()
        const offlineVenueContainer = offlineVenueTitle.closest('div')
        expect(
          within(offlineVenueContainer).getByText('Modifier', { exact: false })
        ).toBeInTheDocument()
      })
    })
  })
})

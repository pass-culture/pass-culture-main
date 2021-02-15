import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Homepage from '../Homepage'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/offerer/demarchesSimplifiees/procedure',
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
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

describe('homepage', () => {
  let baseOfferers
  let baseOfferersNames

  beforeEach(() => {
    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        city: 'Cayenne',
        name: 'Bar des amis',
        id: 'GE',
        postalCode: '97300',
        siren: '111111111',
        bic: 'test bic 01',
        iban: 'test iban 01',
        managedVenues: [
          {
            id: 'test_venue_id_1',
            isVirtual: true,
            managingOffererId: 'GE',
            name: 'Le Sous-sol (Offre numérique)',
            offererName: 'Bar des amis',
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_2',
            isVirtual: false,
            managingOffererId: 'GE',
            name: 'Le Sous-sol (Offre physique)',
            offererName: 'Bar des amis',
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_3',
            isVirtual: false,
            managingOffererId: 'GE',
            name: 'Le deuxième Sous-sol (Offre physique)',
            offererName: 'Bar des amis',
            publicName: 'Le deuxième Sous-sol',
            nOffers: 2,
          },
        ],
      },
      {
        address: 'RUE DE NIEUPORT',
        city: 'Drancy',
        id: 'FQ',
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        bic: 'test bic 02',
        iban: 'test iban 02',
        managedVenues: [],
      },
    ]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
    }))

    pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
    pcapi.getAllOfferersNames.mockResolvedValue(baseOfferersNames)
    pcapi.getVenueStats.mockResolvedValue({ activeBookingsCount: 4 })
  })

  afterEach(() => {
    pcapi.getOfferer.mockClear()
    pcapi.getAllOfferersNames.mockClear()
  })

  describe('render', () => {
    beforeEach(async () => {
      await renderHomePage()
    })

    describe('profileAndSupport', () => {
      it('should display section and subsection titles', () => {
        expect(screen.getByText('Profil et aide', { selector: 'h2' })).toBeInTheDocument()
        expect(screen.getByText('Profil')).toBeInTheDocument()
        expect(screen.getByText('Aide et support')).toBeInTheDocument()
        expect(screen.getByText('Modalités d’usage', { selector: 'h2' })).toBeInTheDocument()
      })

      it('should display help links', () => {
        const contactLink = screen.getByText('Contacter le support', { selector: 'a' })
        const cguLink = screen.getByText('Conditions Générales d’Utilisation', {
          selector: 'a',
        })
        const faqLink = screen.getByText('Foire Aux Questions', { selector: 'a' })

        expect(contactLink).toBeInTheDocument()
        expect(cguLink).toBeInTheDocument()
        expect(faqLink).toBeInTheDocument()

        expect(contactLink.getAttribute('href')).toBe('mailto:support@passculture.app')
        expect(cguLink.getAttribute('href')).toBe('https://pass.culture.fr/cgu-professionnels/')
        expect(faqLink.getAttribute('href')).toBe(
          'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
        )
      })
    })

    it('should display first offerer informations', async () => {
      const selectedOfferer = baseOfferers[0]
      const selectedOffererAddress = `${selectedOfferer.address} ${selectedOfferer.postalCode} ${selectedOfferer.city}`
      expect(await screen.findByText(selectedOfferer.siren)).toBeInTheDocument()
      expect(
        await screen.findByText(selectedOfferer.name, { selector: 'span' })
      ).toBeInTheDocument()
      expect(await screen.findByText(selectedOffererAddress)).toBeInTheDocument()
    })

    it('should display first offerer bank information', async () => {
      const selectedOfferer = baseOfferers[0]
      expect(await screen.findByText(selectedOfferer.iban)).toBeInTheDocument()
      expect(await screen.findByText(selectedOfferer.bic)).toBeInTheDocument()
    })

    it('should display offerer venues informations', async () => {
      const selectedOfferer = baseOfferers[0]
      const virtualVenueTitle = await screen.findByText('Lieu numérique')
      expect(virtualVenueTitle).toBeInTheDocument()

      const offlineVenueTitle = await screen.findByText(selectedOfferer.managedVenues[1].name)
      expect(offlineVenueTitle).toBeInTheDocument()
      const offlineVenueContainer = offlineVenueTitle.closest('div')
      expect(
        within(offlineVenueContainer).getByText('Modifier', { exact: false })
      ).toBeInTheDocument()

      const secondOfflineVenueTitle = await screen.findByText(
        selectedOfferer.managedVenues[2].publicName
      )
      expect(secondOfflineVenueTitle).toBeInTheDocument()
    })

    describe('when selected offerer change', () => {
      let newSelectedOfferer
      beforeEach(async () => {
        const selectedOffer = baseOfferers[0]
        newSelectedOfferer = {
          ...baseOfferers[1],
          managedVenues: [
            {
              id: 'test_venue_id_3',
              isVirtual: true,
              managingOffererId: baseOfferers[1].id,
              name: 'New venue (Offre numérique)',
              offererName: baseOfferers[1].name,
              publicName: null,
              nOffers: 2,
            },
            {
              id: 'test_venue_id_4',
              isVirtual: false,
              managingOffererId: baseOfferers[1].id,
              name: 'New venue (Offre physique)',
              offererName: baseOfferers[1].name,
              publicName: null,
              nOffers: 2,
            },
            {
              id: 'test_venue_id_5',
              isVirtual: false,
              managingOffererId: baseOfferers[1].id,
              name: 'Second new venue (Offre physique)',
              offererName: baseOfferers[1].name,
              publicName: 'Second new venue public name',
              nOffers: 2,
            },
          ],
        }
        pcapi.getOfferer.mockResolvedValue(newSelectedOfferer)
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
          await screen.findByText(newSelectedOfferer.name, { selector: 'span' })
        ).toBeInTheDocument()
        expect(await screen.findByText(selectedOffererAddress)).toBeInTheDocument()
      })

      it('should change displayed bank information', async () => {
        expect(await screen.findByText(newSelectedOfferer.iban)).toBeInTheDocument()
        expect(await screen.findByText(newSelectedOfferer.bic)).toBeInTheDocument()
      })

      it('should display new offerer venues informations', async () => {
        const virtualVenueTitle = await screen.findByText('Lieu numérique')
        expect(virtualVenueTitle).toBeInTheDocument()

        const offlineVenueTitle = await screen.findByText(newSelectedOfferer.managedVenues[1].name)
        expect(offlineVenueTitle).toBeInTheDocument()
        const offlineVenueContainer = offlineVenueTitle.closest('div')
        expect(
          within(offlineVenueContainer).getByText('Modifier', { exact: false })
        ).toBeInTheDocument()

        const secondOfflineVenueTitle = await screen.findByText(
          newSelectedOfferer.managedVenues[2].publicName
        )
        expect(secondOfflineVenueTitle).toBeInTheDocument()
      })
    })
  })

  describe("when offerer doesn't have neither physical venue nor virtual offers", () => {
    it('should display add information link', async () => {
      baseOfferers = [
        {
          ...baseOfferers[0],
          managedVenues: [
            {
              id: 'test_venue_id_1',
              isVirtual: true,
              managingOffererId: 'GE',
              name: 'Le Sous-sol (Offre numérique)',
              offererName: 'Bar des amis',
              publicName: null,
              nOffers: 0,
            },
          ],
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      expect(
        await screen.findByRole('link', {
          name: 'Créer un lieu',
        })
      ).toBeInTheDocument()
      expect(
        await screen.findByRole('link', {
          name: 'Créer une offre numérique',
        })
      ).toBeInTheDocument()
    })
  })

  describe("when offerer doesn't have bank informations", () => {
    it('should display add information link', async () => {
      baseOfferers = [
        {
          ...baseOfferers[0],
          bic: '',
          iban: '',
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      const link = await screen.findByRole('link', {
        name: 'Renseignez les coordonnées bancaires de la structure',
      })
      expect(link).toBeInTheDocument()
      const warningIcons = await screen.findAllByAltText('Informations bancaires manquantes')
      let nbWarningIcons = 0
      nbWarningIcons += 1 // in offerers header
      nbWarningIcons += 1 // in bank account card title
      expect(warningIcons).toHaveLength(nbWarningIcons)
    })

    it("shouldn't display bank warning if all venues have bank informations", async () => {
      baseOfferers = [
        {
          ...baseOfferers[0],
          bic: '',
          iban: '',
          managedVenues: baseOfferers[0].managedVenues.map(venue => {
            return {
              ...venue,
              bic: 'fake_bic',
              iban: 'fake_iban',
            }
          }),
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      const warningIcons = await screen.queryByAltText('Informations bancaires manquantes')
      expect(warningIcons).not.toBeInTheDocument()
    })

    it('should display file information for pending registration', async () => {
      baseOfferers = [
        {
          ...baseOfferers[0],
          bic: '',
          iban: '',
          demarchesSimplifieesApplicationId: 'demarchesSimplifieesApplication_fake_id',
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      expect(await screen.findByRole('link', { name: 'Voir le dossier' })).toBeInTheDocument()
      const warningIcons = await screen.queryByAltText('Informations bancaires manquantes')
      expect(warningIcons).not.toBeInTheDocument()
    })

    describe('profile section', () => {
      it('should display profile informations', async () => {
        // then
        expect(await screen.findByText('Nom :')).toBeInTheDocument()
        expect(await screen.findByText('Do')).toBeInTheDocument()
        expect(await screen.findByText('Prénom :')).toBeInTheDocument()
        expect(await screen.findByText('John')).toBeInTheDocument()
        expect(await screen.findByText('E-mail :')).toBeInTheDocument()
        expect(await screen.findByText('john.do@dummy.xyz')).toBeInTheDocument()
        expect(await screen.findByText('Téléphone :')).toBeInTheDocument()
        expect(await screen.findByText('01 00 00 00 00')).toBeInTheDocument()
      })

      it('should display profile modifications modal when clicking on modify button', async () => {
        // when
        fireEvent.click(screen.getByText('Modifier', { selector: 'button' }))

        // then
        const lastNameInput = await screen.findByLabelText('Nom')
        const firstNameInput = await screen.findByLabelText('Prénom')
        const emailInput = await screen.findByLabelText('Email')
        const phoneInput = await screen.findByLabelText('Téléphone')
        expect(lastNameInput).toBeInTheDocument()
        expect(firstNameInput).toBeInTheDocument()
        expect(emailInput).toBeInTheDocument()
        expect(phoneInput).toBeInTheDocument()
      })
    })
  })
})

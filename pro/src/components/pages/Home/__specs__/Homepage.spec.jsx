/*
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 * @debt rtl "Gaël: this file contains eslint error(s) based on eslint-testing-library plugin"
 * @debt rtl "Gaël: bad use of act in testing library"
 */

import '@testing-library/jest-dom'
import { act, render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import Homepage from '../Homepage'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/offerer/demarchesSimplifiees/procedure',
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
  updateUserInformations: jest.fn().mockResolvedValue({}),
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn(),
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
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        bic: 'test bic 01',
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
        iban: 'test iban 01',
        id: 'GE',
        isValidated: true,
        lastProviderId: null,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '111111111',
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
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        bic: 'test bic 02',
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
        iban: 'test iban 02',
        id: 'FQ',
        isValidated: true,
        lastProviderId: null,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [],
      },
    ]

    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
    }))

    pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
    pcapi.getAllOfferersNames.mockResolvedValue(baseOfferersNames)
    pcapi.getVenueStats.mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
  })

  describe('render', () => {
    beforeEach(async () => {
      await renderHomePage()
    })

    describe('when clicking on anchor link to profile', () => {
      let scrollIntoViewMock
      beforeEach(() => {
        scrollIntoViewMock = jest.fn()
        Element.prototype.scrollIntoView = scrollIntoViewMock
      })

      it('should smooth scroll to section if user doesnt prefer reduced motion', () => {
        // given
        doesUserPreferReducedMotion.mockReturnValue(false)

        // when
        fireEvent.click(screen.getByRole('link', { name: 'Profil et aide' }))

        // then
        expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' })
      })

      it('should jump to section if user prefers reduced motion', () => {
        // given
        doesUserPreferReducedMotion.mockReturnValue(true)

        // when
        fireEvent.click(screen.getByRole('link', { name: 'Profil et aide' }))

        // then
        expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'auto' })
      })
    })

    describe('profileAndSupport', () => {
      it('should display section and subsection titles', () => {
        expect(
          screen.getByText('Profil et aide', { selector: 'h2' })
        ).toBeInTheDocument()
        expect(screen.getByText('Profil')).toBeInTheDocument()
        expect(screen.getByText('Aide et support')).toBeInTheDocument()
      })

      describe('update profile informations modal', () => {
        it('should display profile modifications modal when clicking on modify button', async () => {
          // when
          fireEvent.click(screen.getByText('Modifier', { selector: 'button' }))

          // then
          await expect(
            screen.findByLabelText('Nom')
          ).resolves.toBeInTheDocument()
          await expect(
            screen.findByLabelText('Prénom')
          ).resolves.toBeInTheDocument()
          await expect(
            screen.findByLabelText('Email')
          ).resolves.toBeInTheDocument()
          await expect(
            screen.findByLabelText('Téléphone')
          ).resolves.toBeInTheDocument()
        })

        it('should close the modal when clicking on cancel button', async () => {
          // given
          fireEvent.click(screen.getByText('Modifier', { selector: 'button' }))

          // when
          fireEvent.click(screen.getByText('Annuler', { selector: 'button' }))

          // then
          await waitFor(() =>
            expect(screen.queryByLabelText('Nom')).not.toBeInTheDocument()
          )
        })

        it('should update user info on submit', async () => {
          // given
          fireEvent.click(screen.getByText('Modifier', { selector: 'button' }))
          fireEvent.change(screen.getByLabelText('Prénom'), {
            target: { value: 'Johnny' },
          })
          fireEvent.change(screen.getByLabelText('Nom'), {
            target: { value: 'Doe' },
          })
          fireEvent.change(screen.getByLabelText('Email'), {
            target: { value: 'johnny.doe@dummy.xyz' },
          })
          fireEvent.change(screen.getByLabelText('Téléphone'), {
            target: { value: '01 01 00 00 00' },
          })

          // when
          await act(async () => {
            await fireEvent.click(
              screen.getByRole('button', { name: 'Enregistrer' })
            )
          })

          // then
          expect(pcapi.updateUserInformations).toHaveBeenCalledWith({
            firstName: 'Johnny',
            lastName: 'Doe',
            email: 'johnny.doe@dummy.xyz',
            phoneNumber: '01 01 00 00 00',
          })
        })

        it('should show errors on submit', async () => {
          // given
          pcapi.updateUserInformations.mockRejectedValue({
            errors: {
              firstName: ['Prénom en erreur'],
              email: ['Email en erreur'],
            },
          })
          fireEvent.click(screen.getByText('Modifier', { selector: 'button' }))
          fireEvent.change(screen.getByLabelText('Prénom'), {
            target: { value: 'Johnny' },
          })
          fireEvent.change(screen.getByLabelText('Email'), {
            target: { value: 'johnny.doe@dummy.xyz' },
          })

          // when
          await act(async () => {
            await fireEvent.click(
              screen.getByRole('button', { name: 'Enregistrer' })
            )
          })

          // then
          expect(screen.getByText('Prénom en erreur')).toBeInTheDocument()
          expect(screen.getByText('Email en erreur')).toBeInTheDocument()
        })
      })
    })
  })
})

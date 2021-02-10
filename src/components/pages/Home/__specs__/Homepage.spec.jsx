import '@testing-library/jest-dom'
import { act, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'

import Homepage from '../Homepage'

jest.mock('repository/pcapi/pcapi', () => ({
  getValidatedOfferers: jest.fn(),
}))

const renderHomePage = async () => {
  return await act(async () => {
    await render(
      <MemoryRouter>
        <Homepage />
      </MemoryRouter>
    )
  })
}

describe('homepage : Tabs : Offerers', () => {
  let baseOfferers

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
    pcapi.getValidatedOfferers.mockResolvedValue(baseOfferers)
  })

  afterEach(() => {
    pcapi.getValidatedOfferers.mockClear()
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

    describe('when selected offerer change', () => {
      let newSelectedOfferer
      beforeEach(async () => {
        const selectedOffer = baseOfferers[0]
        newSelectedOfferer = baseOfferers[1]
        await fireEvent.change(screen.getByDisplayValue(selectedOffer.name), {
          target: { value: newSelectedOfferer.id },
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
    })
  })
})

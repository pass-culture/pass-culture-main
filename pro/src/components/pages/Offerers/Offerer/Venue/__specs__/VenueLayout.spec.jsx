import '@testing-library/jest-dom'

import { act, render, screen } from '@testing-library/react'

import { MemoryRouter } from 'react-router'
import React from 'react'
import { Route } from 'react-router-dom'
import VenueLayout from '../VenueLayout'
import { fireEvent } from '@testing-library/dom'

const renderVenueLayout = async (offererId, url = '/') => {
  const baseUrl = `/structures/${offererId}/lieux`
  const basePath = '/structures/:offererId([A-Z0-9]+)/lieux'
  url = `${baseUrl}${url}`

  await act(async () => {
    await render(
      <MemoryRouter initialEntries={[{ pathname: url }]} initialIndex={0}>
        <Route path={basePath}>
          <VenueLayout />
        </Route>
        <Route>DO NOT MATCH</Route>
      </MemoryRouter>
    )
  })
}

describe('testing VenueLayout', () => {
  let offerer
  let venue

  beforeEach(() => {
    offerer = {
      id: 'fakeOffererId',
    }
    venue = {
      id: 'fakeVenueId',
    }
  })

  describe('testing venue creation', () => {
    beforeEach(async () => {
      await renderVenueLayout(offerer.id, '/creation')
    })

    it('should render venue creation page', () => {
      expect(screen.getByText('Créer un lieu')).toBeInTheDocument()
    })

    it('should display default tab "Informations"', () => {
      expect(
        screen.getByText('create venue information form')
      ).toBeInTheDocument()
    })

    it('should navigate to "Gestions" tab on click', async () => {
      const tabManagement = screen.getByText('Gestions')
      await act(async () => {
        await fireEvent.click(tabManagement)
      })

      expect(
        screen.getByText('create venue management form')
      ).toBeInTheDocument()
    })
  })

  describe('testing temporary venue creation', () => {
    beforeEach(async () => {
      await renderVenueLayout(offerer.id, '/temporaire/creation')
    })

    it('should render temporary venue creation', async () => {
      expect(screen.getByText('Créer un lieu temporaire')).toBeInTheDocument()
    })

    it('should display default tab "Informations"', () => {
      expect(
        screen.getByText('create temporary venue information form')
      ).toBeInTheDocument()
    })

    it('should navigate to "Gestions" tab on click', async () => {
      const tabManagement = screen.getByText('Gestions')
      await act(async () => {
        await fireEvent.click(tabManagement)
      })

      expect(
        screen.getByText('create venue management form')
      ).toBeInTheDocument()
    })
  })

  describe('testing venue edition', () => {
    beforeEach(async () => {
      await renderVenueLayout(offerer.id, `/${venue.id}`)
    })

    it('should render venue edition', async () => {
      expect(screen.getByText('Editer votre lieu')).toBeInTheDocument()
    })

    it('should display default tab "Informations"', () => {
      expect(
        screen.getByText('edit venue information form')
      ).toBeInTheDocument()
    })

    it('should navigate to "Gestions" tab on click', async () => {
      const tabManagement = screen.getByText('Gestions')
      await act(async () => {
        await fireEvent.click(tabManagement)
      })

      expect(screen.getByText('edit venue management form')).toBeInTheDocument()
    })
  })
})

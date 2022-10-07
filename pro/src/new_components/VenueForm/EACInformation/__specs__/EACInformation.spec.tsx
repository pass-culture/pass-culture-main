import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { IVenue } from 'core/Venue'
import { configureTestStore } from 'store/testUtils'

import EACInformation from '../EACInformation'

const CREATION_TEXT = /Renseigner mes informations/
const UPDATE_TEXT = /Modifier mes informations/
const INFORMATION_BANNER_TEXT = /Une fois votre lieu créé/

const renderEACInformation = async ({
  venue,
  isCreatingVenue,
}: {
  venue?: IVenue | null
  isCreatingVenue: boolean
}) => {
  render(
    <Router history={createBrowserHistory()}>
      <Provider store={configureTestStore({})}>
        <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
      </Provider>
    </Router>
  )
}

describe('components | EACInformation', () => {
  it('should have the button disabled', async () => {
    await renderEACInformation({
      isCreatingVenue: true,
      venue: null,
    })

    expect(screen.queryByText(CREATION_TEXT)).toHaveAttribute(
      'aria-disabled',
      'true'
    )
  })

  it('should have the button with creation text with empty details', async () => {
    const venue = {
      id: 'V1',
    } as unknown as IVenue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(await screen.queryByText(CREATION_TEXT)).toBeInTheDocument()
  })

  it('should have the button with update text', async () => {
    const venue = {
      id: 'V1',
      collectiveAccessInformation: 'test',
      collectiveDescription: 'desc',
      collectiveEmail: 'email@email.email',
    } as unknown as IVenue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(await screen.queryByText(UPDATE_TEXT)).toBeInTheDocument()
  })

  it('should have the information banner', async () => {
    await renderEACInformation({
      isCreatingVenue: true,
      venue: null,
    })

    expect(
      await screen.queryByText(INFORMATION_BANNER_TEXT)
    ).toBeInTheDocument()
  })

  it('should not have the information banner', async () => {
    const venue = {
      id: 'V1',
      collectiveAccessInformation: 'test',
      collectiveDescription: 'desc',
      collectiveEmail: 'email@email.email',
    } as unknown as IVenue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(
      await screen.queryByText(INFORMATION_BANNER_TEXT)
    ).not.toBeInTheDocument()
  })
})

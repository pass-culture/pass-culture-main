import { screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueFormActionBar } from '../index'

const renderVanueFormActionBar = ({
  isCreatingVenue,
}: {
  isCreatingVenue: boolean
}) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        nonHumanizedId: 12,
        isAdmin: true,
      },
    },
    features: {
      list: [
        {
          nameKey: 'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
          isActive: true,
        },
      ],
      initialized: true,
    },
  }

  renderWithProviders(
    <Formik initialValues={{}} onSubmit={jest.fn()}>
      <VenueFormActionBar isCreatingVenue={isCreatingVenue} offererId={59} />
    </Formik>,
    { storeOverrides }
  )
}
jest.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({ remoteConfig: {} }),
}))

jest.mock('hooks/useNewOfferCreationJourney', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false),
}))

jest.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

describe('VenueFormActionBar', () => {
  it('should display right message on creation', async () => {
    jest.mock('@firebase/remote-config', () => ({
      getValue: () => ({ asBoolean: () => false }),
    }))

    renderVanueFormActionBar({ isCreatingVenue: true })
    expect(screen.getByText('Enregistrer et continuer')).toBeInTheDocument()
  })

  it('should display right message on edition', async () => {
    renderVanueFormActionBar({ isCreatingVenue: false })
    expect(screen.getByText('Enregistrer et quitter')).toBeInTheDocument()
  })

  describe('with ab testing', () => {
    beforeEach(() => {
      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
    })
    it('should display right message on creation with a/b testing access', async () => {
      renderVanueFormActionBar({ isCreatingVenue: true })
      expect(
        screen.getByText('Enregistrer et créer le lieu')
      ).toBeInTheDocument()
    })
  })
})

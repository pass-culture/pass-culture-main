import { screen } from '@testing-library/react'
import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import { INITIAL_OFFERER_VENUES } from 'pages/Home/OffererVenues'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offerers from '../Offerers'

const selectedOfferer: GetOffererResponseModel = {
  address: null,
  apiKey: {
    maxAllowed: 0,
    prefixes: [],
  },
  city: 'city',
  dateCreated: '1010/10/10',
  dateModifiedAtLastProvider: null,
  demarchesSimplifieesApplicationId: null,
  fieldsUpdated: [],
  hasAvailablePricingPoints: false,
  hasDigitalVenueAtLeastOneOffer: false,
  id: 'id',
  idAtProviders: null,
  isActive: false,
  isValidated: false,
  lastProviderId: null,
  managedVenues: [],
  name: 'name',
  nonHumanizedId: 10,
  postalCode: '123123',
  siren: null,
}
const renderOfferers = async (userOffererValidated: boolean) => {
  renderWithProviders(
    <Offerers
      receivedOffererNames={{
        offerersNames: [{ id: 'idd', name: 'name', nonHumanizedId: 1 }],
      }}
      onSelectedOffererChange={() => null}
      cancelLoading={() => null}
      selectedOfferer={selectedOfferer}
      isLoading={false}
      isUserOffererValidated={userOffererValidated}
      venues={INITIAL_OFFERER_VENUES}
    />
  )
}

describe('Offerers', () => {
  it('should not display venue soft deleted if user is not validated', async () => {
    await renderOfferers(false)
    expect(
      screen.getByText(
        /Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture/
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).not.toBeInTheDocument()
  })

  it('should display venue soft deleted', async () => {
    await renderOfferers(true)
    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).toBeInTheDocument()
  })
})

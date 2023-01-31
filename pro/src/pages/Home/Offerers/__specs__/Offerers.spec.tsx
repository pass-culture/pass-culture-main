import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { api } from '../../../../apiClient/api'
import Offerers from '../Offerers'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
  },
}))

const renderOfferers = async () => {
  renderWithProviders(
    <Offerers
      receivedOffererNames={{
        offerersNames: [{ id: 'idd', name: 'name', nonHumanizedId: 1 }],
      }}
    />
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'), {
    timeout: 20000,
  })
}

describe('Offerers', () => {
  beforeEach(async () => {
    jest.spyOn(api, 'getOfferer').mockRejectedValue({ status: 403 })
  })

  it('should not display venue soft deleted if user is not validated', async () => {
    await renderOfferers()
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
})

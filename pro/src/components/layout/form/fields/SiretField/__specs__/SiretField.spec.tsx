import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'

import { apiAdresse } from 'apiClient/adresse'
import { IAdresseData } from 'apiClient/adresse/types'
import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { configureTestStore } from 'store/testUtils'

import SiretField from '../SiretField'
import siretApiValidate from '../validators/siretApiValidate'

jest.mock('apiClient/adresse', () => {
  return {
    ...jest.requireActual('apiClient/adresse'),
    default: {
      getDataFromAddress: jest.fn(),
    },
  }
})

const addressApiDataMock: IAdresseData = {
  address: '3 Rue de Valois',
  city: 'Paris',
  id: '75101_9575_00003',
  latitude: 1.9,
  longitude: 1.8,
  label: '3 Rue de Valois 75001 Paris',
  postalCode: '75001',
}

describe('components | SiretField', () => {
  beforeEach(() => {
    jest
      .spyOn(apiAdresse, 'getDataFromAddress')
      .mockResolvedValue([addressApiDataMock])
  })

  it('should display a error if siret do not include given siren', async () => {
    const siren = '000000000'
    const wrongSiret = '11111111199999'
    jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
      name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
      siret: wrongSiret,
      active: true,
      address: {
        street: '19 RUE LAITIERE',
        city: 'BAYEUX',
        postalCode: '14400',
      },
    })
    const store = configureTestStore()
    render(
      <Provider store={store}>
        <Form initialValues={{}} name="venue" onSubmit={() => {}}>
          {() => (
            <SiretField
              siren={siren}
              readOnly={false}
              label="Siret field"
              required
            />
          )}
        </Form>
      </Provider>
    )
    const siretField = screen.getByLabelText('Siret field*')
    expect(siretField).toBeInTheDocument()

    const wrongSiretMsg =
      'Le code SIRET doit correspondre à un établissement de votre structure'
    await userEvent.type(siretField, wrongSiret)
    await userEvent.tab()
    expect(screen.getByText(wrongSiretMsg)).toBeInTheDocument()

    const validSiret = '00000000099999'
    await userEvent.clear(siretField)
    await userEvent.type(siretField, validSiret)
    await userEvent.tab()
    expect(screen.queryByText(wrongSiretMsg)).not.toBeInTheDocument()
  })
  describe('getSiretData', () => {
    it('should not call API when SIRET is empty', async () => {
      // given
      const siret = ''
      jest.spyOn(api, 'getSiretInfo')

      // when
      await getSiretData(siret)

      // then
      expect(api.getSiretInfo).not.toHaveBeenCalled()
    })
    it('should have a latitude and longitude if provided', async () => {
      jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
        name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
        siret: '12345178901834',
        active: true,
        address: {
          street: '19 RUE LAITIERE',
          city: 'BAYEUX',
          postalCode: '14400',
        },
      })

      const siret = '12345178901834'
      const values = await getSiretData(siret)

      expect(values).toStrictEqual({
        isOk: true,
        message: `Informations récupéré avec success pour le SIRET: ${siret} :`,
        payload: {
          values: {
            address: '19 RUE LAITIERE',
            city: 'BAYEUX',
            latitude: 1.9,
            longitude: 1.8,
            name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            postalCode: '14400',
            siret: siret,
          },
        },
      })
    })
  })
  describe('siretApiValidate', () => {
    it('should call the INSEE API with the formatted SIRET', async () => {
      // given
      jest.spyOn(api, 'getSiretInfo').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 404,
            body: {
              global: ['no results foud'],
            },
          } as ApiResult,
          ''
        )
      )
      const siret = '12345678901234'
      const humanSiret = '123 456 789 01234'

      // when
      await siretApiValidate(humanSiret)

      // then
      expect(api.getSiretInfo).toHaveBeenCalledTimes(1)
      expect(api.getSiretInfo).toHaveBeenCalledWith(
        expect.stringContaining(`${siret}`)
      )
    })
    it('should not return an error message when SIRET exists in INSEE registry', async () => {
      // given
      const siret = '17345678901734'
      jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
        name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
        siret: '12345178901834',
        active: true,
        address: {
          street: '19 RUE LAITIERE',
          city: 'BAYEUX',
          postalCode: '14400',
        },
      })

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBeUndefined()
    })
    it('should return an error when SIRET is anonymous on INSEE registry', async () => {
      // given
      const siret = '92341678901534'
      jest.spyOn(api, 'getSiretInfo').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              global: [
                'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.',
              ],
            },
          } as ApiResult,
          ''
        )
      )

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe(
        'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
      )
    })
    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siret = '12945678901534'
      jest.spyOn(api, 'getSiretInfo').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              global: ["Ce SIREN ou SIRET n'existe pas."],
            },
          } as ApiResult,
          ''
        )
      )
      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe("Ce SIREN ou SIRET n'existe pas.")
    })
    it('should check once for same SIRET called in INSEE registery', async () => {
      // given
      const siret = '12945678901539'
      jest.spyOn(api, 'getSiretInfo').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              global: ["Ce SIREN ou SIRET n'existe pas."],
            },
          } as ApiResult,
          ''
        )
      )

      // when
      await siretApiValidate(siret)
      await siretApiValidate(siret)

      // then
      expect(api.getSiretInfo).toHaveBeenCalledTimes(1)
      expect(api.getSiretInfo).toHaveBeenCalledWith(
        expect.stringContaining(`${siret}`)
      )
    })
  })
})

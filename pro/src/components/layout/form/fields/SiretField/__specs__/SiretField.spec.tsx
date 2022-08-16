import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'

import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { configureTestStore } from 'store/testUtils'

import SiretField from '../SiretField'
import siretApiValidate from '../validators/siretApiValidate'

const addressApiDataMock = {
  features: [
    {
      geometry: { type: 'Point', coordinates: [1.9, 1.9] },
      properties: {
        label: '3 Rue de Valois 75001 Paris',
        id: '75101_9575_00003',
        name: '3 Rue de Valois',
        postcode: '75001',
        city: 'Paris',
      },
    },
  ],
}

describe('components | SiretField', () => {
  it('should display a error if siret do not include given siren', async () => {
    const siren = '000000000'
    fetch.mockResponseOnce('')
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

    const wrongSiret = '11111111199999'
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
    beforeEach(() => {
      fetch.resetMocks()
    })
    it('should not call API when SIRET is empty', async () => {
      // given
      const siret = ''

      // when
      await getSiretData(siret)

      // then
      expect(fetch).not.toHaveBeenCalled()
    })
    it('should have a latitude and longitude if provided', async () => {
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            siret: '12345178901834',
            active: true,
            address: {
              street: '19 RUE LAITIERE',
              city: 'BAYEUX',
              postalCode: '14400',
            },
          }),
      })
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () => Promise.resolve(addressApiDataMock),
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
            longitude: 1.9,
            name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            postalCode: '14400',
            siret: siret,
          },
        },
      })
    })
  })
  describe('siretApiValidate', () => {
    beforeEach(() => {
      fetch.resetMocks()
    })

    it('should call the INSEE API with the formatted SIRET', async () => {
      // given
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })
      const siret = '12345678901234'
      const humanSiret = '123 456 789 01234'

      // when
      await siretApiValidate(humanSiret)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sirene/siret/${siret}`),
        expect.anything()
      )
    })
    it('should not return an error message when SIRET exists in INSEE registry', async () => {
      // given
      const siret = '17345678901734'
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            siret: '12345178901834',
            active: true,
            address: {
              street: '19 RUE LAITIERE',
              city: 'BAYEUX',
              postalCode: '14400',
            },
          }),
      })
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () => Promise.resolve(addressApiDataMock),
      })

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBeUndefined()
    })
    it('should return an error when SIRET is anonymous on INSEE registry', async () => {
      // given
      const siret = '92341678901534'
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: [
              'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.',
            ],
          }),
      })

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
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: ["Ce SIREN ou SIRET n'existe pas."],
          }),
      })

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe("Ce SIREN ou SIRET n'existe pas.")
    })
    it('should check once for same SIRET called in INSEE registery', async () => {
      // given
      const siret = '12945678901539'
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: ["Ce SIREN ou SIRET n'existe pas."],
          }),
      })

      // when
      await siretApiValidate(siret)
      await siretApiValidate(siret)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sirene/siret/${siret}`),
        expect.anything()
      )
    })
  })
})

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
    it('should have a latitude and longitude if provided', async () => {
      fetch.mockResponseOnce(
        JSON.stringify({
          etablissement: {
            geo_l4: '19 RUE LAITIERE',
            libelle_commune: 'BAYEUX',
            latitude: null,
            longitude: null,
            enseigne_1: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            code_postal: '14400',
            siret: '12345178901834',
            etat_administratif: 'A',
            unite_legale: {
              etat_administratif: 'A',
              etablissement_siege: {
                geo_l4: '19 RUE LAITIERE',
                longitude: '1.9',
                latitude: '1.9',
              },
            },
          },
        })
      )
      const siret = '12345178901834'
      const values = await getSiretData(siret)

      expect(values).toStrictEqual({
        isOk: true,
        message: `Informations récupéré avec success pour le SIRET: ${siret} :`,
        payload: {
          values: {
            address: '19 RUE LAITIERE',
            city: 'BAYEUX',
            companyStatus: 'A',
            latitude: 1.9,
            legalUnitStatus: 'A',
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
        `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
      )
    })
    it('should not return an error message when SIRET exists in INSEE registry', async () => {
      // given
      const siret = '17345678901734'
      fetch.mockResponseOnce(
        JSON.stringify({
          etablissement: {
            geo_l4: '19 RUE LAITIERE',
            libelle_commune: 'BAYEUX',
            latitude: null,
            longitude: null,
            enseigne_1: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            code_postal: '14400',
            siret: '17345678901734',
            etat_administratif: 'A',
            unite_legale: {
              etat_administratif: 'A',
              etablissement_siege: {},
            },
          },
        })
      )

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBeUndefined()
    })
    it('should not return an error message when SIRET exists in INSEE registry without etablissement.geo_l4', async () => {
      // given
      const siret = '12345678101234'
      fetch.mockResponseOnce(
        JSON.stringify({
          etablissement: {
            libelle_commune: 'BAYEUX',
            latitude: null,
            longitude: null,
            enseigne_1: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            code_postal: '14400',
            siret: '12345678101234',
            etat_administratif: 'A',
            unite_legale: {
              etat_administratif: 'A',
              etablissement_siege: {
                geo_l4: '19 RUE LAITIERE',
              },
            },
          },
        })
      )

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBeUndefined()
    })
    it('should return an adresse when SIRET exists in INSEE registry without any geo_l4', async () => {
      // given
      const siret = '12345678101234'
      fetch.mockResponseOnce(
        JSON.stringify({
          etablissement: {
            libelle_commune: 'BAYEUX',
            latitude: null,
            longitude: null,
            enseigne_1: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
            code_postal: '14400',
            siret: '12345678101234',
            etat_administratif: 'A',
            unite_legale: {
              etat_administratif: 'A',
              etablissement_siege: {
                geo_l4: null,
                geo_adresse: 'Place du 8 Mai 1945 (Parc) Saint-Savin',
              },
            },
          },
        })
      )

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBeUndefined()
    })
    it('should return another error message when API returns a status code >=400 and != 404', async () => {
      // given
      const siret = '12345678901534'
      fetch.mockResponseOnce(JSON.stringify({ message: 'Gateway timeout' }), {
        status: 504,
      })

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe(
        'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
      )
    })
    it('should return an error when SIRET is anonymous on INSEE registry', async () => {
      // given
      const siret = '92341678901534'
      fetch.mockResponseOnce(
        JSON.stringify({
          etablissement: {
            statut_diffusion: 'N',
          },
        })
      )

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe(
        'Ce SIRET est masqué sur le répertoire de l’INSEE.'
      )
    })
    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siret = '12945678901534'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      const errorMessage = await siretApiValidate(siret)

      // then
      expect(errorMessage).toBe("Ce SIRET n'est pas reconnu")
    })
    it('should check once for same SIRET called in INSEE registery', async () => {
      // given
      const siret = '12945678901539'
      fetch.mockResponse(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      await siretApiValidate(siret)
      await siretApiValidate(siret)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
      )
    })
  })
})

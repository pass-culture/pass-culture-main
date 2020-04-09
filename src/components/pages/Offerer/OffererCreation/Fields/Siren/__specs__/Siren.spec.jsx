import React from 'react'
import { shallow } from 'enzyme'
import Siren, { existsInINSEERegistry } from '../Siren'

describe('src | components | pages | Offerer | OffererCreation | Fields | Siren', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Siren />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('existsInINSEERegistry', () => {
    beforeEach(() => {
      fetch.resetMocks()
    })

    it('should call the INSEE API with the formatted SIREN', async () => {
      // given
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), { status: 404 })
      const siren = '245 474 278'

      // when
      await existsInINSEERegistry(siren)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        `https://entreprise.data.gouv.fr/api/sirene/v1/siren/245474278`
      )
    })

    it('should not return an error message when SIREN exists in INSEE registry', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(
        JSON.stringify({
          siege_social: {
            l4_normalisee: '3 rue de la gare',
            libelle_commune: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            l1_normalisee: 'nom du lieu',
            code_postal: '75000',
            siren: '418166096',
          },
        })
      )

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).not.toBeDefined()
    })

    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), { status: 404 })

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toStrictEqual("Ce SIREN n'est pas reconnu")
    })
  })
})

/* eslint-disable no-use-before-define */
import { mount } from 'enzyme'
import React from 'react'
import { Field, Form } from 'react-final-form'

import bindGetSiretInfoToSiret from '../bindGetSiretInfoToSiret'

const NAME = 'foo'
const SIRET = '12345678912345'
const mockSuccessSiretInfo = {
  etablissement: {
    code_postal: '75010',
    l1_normalisee: NAME,
    l4_normalisee: "5 cité de l'enfer",
    libelle_commune: 'Paboude',
    latitude: 48.3,
    longitude: 1.2,
    siret: SIRET,
  },
}

global.fetch = url => {
  if (url.includes(SIRET)) {
    const response = new Response(JSON.stringify(mockSuccessSiretInfo))
    return response
  }
}

describe('src | components | pages | Venue | IdentifierFields | bindGetSiretInfoToSiret', () => {
  it('should update the form with siret info', () => {
    // given
    const initialValues = {
      name: null,
      siret: null,
    }
    const wrapper = mount(
      <Form
        decorators={[bindGetSiretInfoToSiret]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field name="siret" render={({ input }) => <input {...input} />} />
            <Field name="name" render={({ input }) => <input {...input} />} />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find(Field)
      .find({ name: 'siret' })
      .find('input')
      .simulate('change', { target: { value: SIRET } })
    setTimeout(() => wrapper.find('button[type="submit"]').simulate('click'))

    // then
    function onSubmit(formValues) {
      const expectedFormValues = {
        name: NAME,
        siret: SIRET,
      }
      expect(formValues).toEqual(expectedFormValues)
    }
  })
})

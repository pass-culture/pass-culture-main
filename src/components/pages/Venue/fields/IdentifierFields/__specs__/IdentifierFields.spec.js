import { shallow } from 'enzyme'
import React from 'react'
import IdentifierFields from '../IdentifierFields'

describe('src | components | pages | Venue | fields | IdentifierFields', () => {
  let props

  beforeEach(() => {
    props = {
      fieldReadOnlyBecauseFrozenFormSiret: true,
      formSiret: 'form siret',
      initialSiret: 'form siret',
      isCreatedEntity: true,
      isModifiedEntity: true,
      readOnly: true
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<IdentifierFields {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})

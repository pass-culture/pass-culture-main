import { shallow } from 'enzyme'
import React from 'react'
import { ApplicationBanner } from '../ApplicationBanner'

describe('when offerer has no bank informations', () => {
  it('should render current application detail', () => {
    // Given
    const props = {
      applicationId: '12',
    }

    // when
    const wrapper = shallow(<ApplicationBanner {...props} />)

    // then
    const bankInstructions = wrapper.find({
      children: 'Votre dossier est en cours pour ce lieu',
    })
    expect(bankInstructions).toHaveLength(1)

    const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
    expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
      'https://www.demarches-simplifiees.fr/dossiers/12'
    )
  })
})

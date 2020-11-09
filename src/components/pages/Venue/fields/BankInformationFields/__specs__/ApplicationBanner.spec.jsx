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
    expect(wrapper.find('Banner').props()).toStrictEqual({
      type: 'attention',
      subtitle: 'Votre dossier est en cours pour ce lieu',
      linkTitle: 'Accéder au dossier',
      href: 'https://www.demarches-simplifiees.fr/dossiers/12',
      icon: 'ico-external-site',
    })
  })
})

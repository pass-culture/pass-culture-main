import { shallow } from 'enzyme'
import React from 'react'

import ApplicationBanner from '../ApplicationBanner'

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
      children:
        'Les coordonnées bancaires de votre lieu sont en cours de validation par notre service financier.',
      linkTitle: 'Voir le dossier en cours',
      href: 'https://www.demarches-simplifiees.fr/dossiers/12',
      type: 'notification-info',
    })
  })
})

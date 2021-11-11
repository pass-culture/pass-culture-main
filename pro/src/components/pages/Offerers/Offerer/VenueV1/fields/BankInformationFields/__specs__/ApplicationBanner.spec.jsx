/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt rtl "Gaël: migration from enzyme to RTL"
 */

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
      closable: false,
      handleOnClick: null,
      type: 'attention',
      children: 'Votre dossier est en cours pour ce lieu',
      linkTitle: 'Accéder au dossier',
      href: 'https://www.demarches-simplifiees.fr/dossiers/12',
      icon: 'ico-external-site',
    })
  })
})

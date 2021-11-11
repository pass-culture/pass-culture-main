import { shallow } from 'enzyme'
import React from 'react'

import SuccessView from '../SuccessView'

describe('src | components | SuccessView', () => {
  it('should display sentences without token', () => {
    // given
    const props = { token: null }

    // when
    const wrapper = shallow(<SuccessView {...props} />)

    // then
    const sentence1 = wrapper.find({
      children: 'Tu vas recevoir un e-mail avec les instructions de réinitialisation.',
    })
    const sentence2 = wrapper.find({
      children:
        'Si tu n’as rien reçu d’ici une heure, merci de vérifier ton e-mail et de le saisir à nouveau.',
    })
    expect(sentence1).toHaveLength(1)
    expect(sentence2).toHaveLength(1)
  })

  it('should display sentence with token', () => {
    // given
    const props = { token: '1234567890' }

    // when
    const wrapper = shallow(<SuccessView {...props} />)

    // then
    const sentence = wrapper.find({
      children: 'Ton mot de passe a bien été enregistré, tu peux l’utiliser pour te connecter',
    })
    expect(sentence).toHaveLength(1)
  })
})

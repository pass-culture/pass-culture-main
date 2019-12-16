import React from 'react'
import { shallow } from 'enzyme'

import BetaPage from '../BetaPage'
import FormFooter from '../../../forms/FormFooter'

describe('components | BetaPage', () => {
  it('should render page component with pass culture information', () => {
    // when
    const wrapper = shallow(<BetaPage />)

    // then
    const divs = wrapper.find('main').find('div')
    expect(divs).toHaveLength(3)
    expect(divs.at(0).text()).toBe('Bienvenue dans\nvotre pass Culture')
    expect(divs.at(1).text()).toBe('Vous avez 18 ans et vivez dans un\ndépartement éligible ?')
    expect(divs.at(2).text()).toBe('Bénéficiez de 500 € afin de\nrenforcer vos pratiques\nculturelles et d\'en découvrir\nde nouvelles !')
  })

  it('should render a FormFooter component with the right props', () => {
    // when
    const wrapper = shallow(<BetaPage />)

    // then
    const footer = wrapper.find(FormFooter)
    expect(footer).toHaveLength(1)
    expect(footer.prop('externalLink')).toStrictEqual({
      id: 'sign-up-link',
      label: 'Créer un compte',
      target: '_blank',
      url: 'https://www.demarches-simplifiees.fr/commencer/inscription-pass-culture'
    })
    expect(footer.prop('submit')).toStrictEqual({
      id: 'sign-in-link',
      label: "J'ai un compte",
      url: '/connexion'
    })
  })
})

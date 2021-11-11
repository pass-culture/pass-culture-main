import React from 'react'
import { mount, shallow } from 'enzyme'

import BetaPage from '../BetaPage'
import { Router } from 'react-router'
import { createBrowserHistory } from 'history'
import {
  APP_NATIVE_DYNAMIC_LINK,
  ANDROID_APP_ID,
  IOS_APP_STORE_ID,
  IOS_APP_ID,
  UNIVERSAL_LINK,
} from '../../../../utils/config'

jest.mock('../../../../notifications/setUpBatchSDK', () => jest.fn())

const openWindowMock = jest.spyOn(window, 'open')

const render = () => {
  const wrapper = shallow(<BetaPage />)
  const findByText = text => wrapper.findWhere(node => node.type() && node.text() === text)
  return {
    instance: wrapper,
    findByText,
  }
}

describe('components | BetaPage', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should render page component with pass culture information', () => {
    const wrapper = render()

    // then
    const line1 = wrapper.findByText('Bienvenue sur\nle pass Culture,')
    const line2 = wrapper.findByText(
      "l'application pour découvrir les activités et\nsorties culturelles proches de chez toi et\npartout en France."
    )
    const line3 = wrapper.findByText(
      "Pour profiter au mieux des fonctionnalités de\nl'application, télécharge-la depuis les stores."
    )
    const line4 = wrapper.findByText(
      'Tu as déjà un compte ?\nConnecte-toi vite pour réserver et profiter de\ntoutes les offres disponibles !'
    )
    expect(line1).toHaveLength(1)
    expect(line2).toHaveLength(1)
    expect(line3).toHaveLength(1)
    expect(line4).toHaveLength(1)
  })

  it('should render an Icon component for page background', () => {
    const wrapper = render()

    // then
    const icon = wrapper.instance.findWhere(node => node.hasClass('bp-logo'))
    expect(icon).toHaveLength(1)
  })

  it('should redirect to sign in page when clicking on sign in button', () => {
    // given
    const history = createBrowserHistory()
    const wrapper = mount(
      <Router history={history}>
        <BetaPage />
      </Router>
    )
    const signInLink = wrapper
      .findWhere(node => node.type && node.text() === 'Se connecter')
      .first()

    // when
    // see issue : shorturl.at/rxCHW
    signInLink.simulate('click', { button: 0 })

    // then
    expect(wrapper.prop('history').location.pathname).toBe('/connexion')
  })

  it('should redirect to app or store when clicking on download app button', () => {
    const wrapper = render()

    // then
    const downloadAppButton = wrapper.instance.findWhere(node =>
      node.hasClass('download-app-button')
    )
    expect(downloadAppButton).toHaveLength(1)

    downloadAppButton.simulate('click', { button: 0 })

    expect(openWindowMock).toHaveBeenCalledWith(
      `${APP_NATIVE_DYNAMIC_LINK}/?link=https://${UNIVERSAL_LINK}/default&apn=${ANDROID_APP_ID}&isi=${IOS_APP_STORE_ID}&ibi=${IOS_APP_ID}&efr=1&ofl=https://pass.culture.fr/nosapplications`
    )
  })
})

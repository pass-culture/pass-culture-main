import React from 'react'
import { mount, shallow } from 'enzyme'

import BetaPage from '../BetaPage'
import { Router } from 'react-router'
import { createBrowserHistory } from 'history'

jest.mock('../../../../notifications/setUpBatchSDK', () => jest.fn())

const openWindowMock = jest.spyOn(window, 'open')

const render = props => {
  const wrapper = shallow(<BetaPage {...props} />)
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
    // when
    const props = {
      isNewBookingLimitsActived: false,
    }
    const wrapper = render(props)

    // then
    const line1 = wrapper.findByText('Bienvenue dans\nton pass Culture')
    const line2 = wrapper.findByText('Tu as 18 ans ?')
    const line3 = wrapper.findByText(
      "Bénéficie de 500 € afin de\nrenforcer tes pratiques\nculturelles et d'en découvrir\nde nouvelles !"
    )
    expect(line1).toHaveLength(1)
    expect(line2).toHaveLength(1)
    expect(line3).toHaveLength(1)
  })

  it('should render page component with 300 € when new booking limits is activated', () => {
    // when
    const props = {
      isNewBookingLimitsActived: true,
    }
    const wrapper = render(props)

    // then
    const line1 = wrapper.findByText('Bienvenue dans\nton pass Culture')
    const line2 = wrapper.findByText('Tu as 18 ans ?')
    const line3 = wrapper.findByText(
      "Bénéficie de 300 € afin de\nrenforcer tes pratiques\nculturelles et d'en découvrir\nde nouvelles !"
    )
    expect(line1).toHaveLength(1)
    expect(line2).toHaveLength(1)
    expect(line3).toHaveLength(1)
  })

  it('should render an Icon component for page background', () => {
    // when
    const props = {
      isNewBookingLimitsActived: true,
    }
    const wrapper = render(props)

    // then
    const icon = wrapper.instance.findWhere(node => node.hasClass('bp-logo'))
    expect(icon).toHaveLength(1)
  })

  it('should redirect to sign in page when clicking on sign in button', () => {
    // given
    const history = createBrowserHistory()
    const props = {
      isNewBookingLimitsActived: true,
    }
    const wrapper = mount(
      <Router history={history}>
        <BetaPage {...props} />
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
    // when
    const props = {
      isNewBookingLimitsActived: true,
    }
    const wrapper = render(props)

    // then
    const downloadAppButton = wrapper.instance.findWhere(node =>
      node.hasClass('download-app-button')
    )
    expect(downloadAppButton).toHaveLength(1)

    downloadAppButton.simulate('click', { button: 0 })

    expect(openWindowMock).toHaveBeenCalledWith(
      'https://passcultureapp.page.link/?link=https://passculture.app/default&apn=app.passculture.webapp&isi=1557887412&ibi=app.passculture&efr=1&ofl=https://pass.culture.fr/nosapplications'
    )
  })
})

import React from 'react'
import { mount, shallow } from 'enzyme'

import BetaPage from '../BetaPage'
import FormFooter from '../../../forms/FormFooter'
import { Router } from 'react-router'
import { createBrowserHistory } from 'history'
import Icon from '../../../layout/Icon/Icon'

jest.mock('../../../../notifications/setUpBatchSDK', () => jest.fn())

describe('components | BetaPage', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should render page component with pass culture information', () => {
    // when
    const props = {
      isNewBookingLimitsActived: false,
      wholeFranceOpening: false,
      trackSignup: jest.fn(),
    }
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const line1 = wrapper.findWhere(node => node.text() === 'Bienvenue dans\nton pass Culture')
    const line2 = wrapper.findWhere(
      node => node.text() === 'Tu as 18 ans et tu vis dans un département éligible ?'
    )
    const line3 = wrapper.findWhere(
      node =>
        node.text() ===
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
      wholeFranceOpening: false,
      trackSignup: jest.fn(),
    }
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const line1 = wrapper.findWhere(node => node.text() === 'Bienvenue dans\nton pass Culture')
    const line2 = wrapper.findWhere(
      node => node.text() === 'Tu as 18 ans et tu vis dans un département éligible ?'
    )
    const line3 = wrapper.findWhere(
      node =>
        node.text() ===
        "Bénéficie de 300 € afin de\nrenforcer tes pratiques\nculturelles et d'en découvrir\nde nouvelles !"
    )
    expect(line1).toHaveLength(1)
    expect(line2).toHaveLength(1)
    expect(line3).toHaveLength(1)
  })

  // FIXME (dbaty, 2020-01-18): once the feature flag is removed, delete tests
  // that have the "[legacy]" tag.
  it('[legacy] should have a link to eligible departments if feature flag is off', () => {
    // when
    const props = {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: false,
      trackSignup: jest.fn(),
    }
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const hasLink = wrapper.findWhere(node => node.text() === 'département éligible').exists()
    expect(hasLink).toBe(true)
  })

  it('[legacy] should not have a link to eligible departments if feature flag is on', () => {
    // when
    const props = {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: true,
      trackSignup: jest.fn(),
    }
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const hasLink = wrapper.findWhere(node => node.text() === 'département éligible').exists()
    expect(hasLink).toBe(false)
  })

  it('should render an Icon component for page background', () => {
    // when
    const props = {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: true,
      trackSignup: jest.fn(),
    }
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const icon = wrapper.find(Icon)
    expect(icon.prop('alt')).toBe('')
    expect(icon.prop('svg')).toBe('circle')
  })

  it('should render a FormFooter component with the right props', () => {
    // given
    const trackSignupMock = jest.fn()
    const props = {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: true,
      trackSignup: trackSignupMock,
    }

    // when
    const wrapper = shallow(<BetaPage {...props} />)

    // then
    const footer = wrapper.find(FormFooter)
    expect(footer).toHaveLength(1)
    expect(footer.prop('items')).toStrictEqual([
      {
        id: 'sign-up-link',
        label: 'Créer un compte',
        tracker: trackSignupMock,
        url: '/verification-eligibilite',
      },
      {
        id: 'sign-in-link',
        label: 'Me connecter',
        url: '/connexion',
      },
    ])
  })

  it('should redirect to sign in page when clicking on sign in link', () => {
    // given
    const history = createBrowserHistory()
    const props = {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: true,
      trackSignup: jest.fn(),
    }
    const wrapper = mount(
      <Router history={history}>
        <BetaPage {...props} />
      </Router>
    )
    const signInLink = wrapper.findWhere(node => node.text() === 'Me connecter').first()

    // when
    // see issue : shorturl.at/rxCHW
    signInLink.simulate('click', { button: 0 })

    // then
    expect(wrapper.prop('history').location.pathname).toBe('/connexion')
  })
})

import { shallow } from 'enzyme'
import React from 'react'
import { Matomo } from '../Matomo'

describe('src | components | hocs | Matomo', () => {
  it('should dispatch a new page displayed event', () => {
    // given
    const fakeMatomoTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoTracker
    const location = {
      pathname: '/router/path',
    }

    // when
    shallow(
      <Matomo location={location}>
        <div>Children</div>
      </Matomo>
    )

    // then
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(1, [
      'setCustomUrl',
      '/router/path',
    ])
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(3, ['trackPageView'])
  })

  it('should dispatch the page title', () => {
    // given
    const fakeMatomoTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoTracker
    document.title = 'PassCulture Page Name'
    const location = {
      pathname: '/router/path',
    }

    // when
    shallow(
      <Matomo location={location}>
        <div>Children</div>
      </Matomo>
    )

    // then
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'PassCulture Page Name',
    ])
  })

  it('should render the children', () => {
    // given
    const location = {
      pathname: '/router/path',
    }

    // when
    const wrapper = shallow(
      <Matomo location={location}>
        <div>Empty</div>
      </Matomo>
    )
    wrapper.setProps({ children: <div>Children</div> })

    // then
    expect(wrapper.html()).toEqual('<div>Children</div>')
  })

  describe('when the location is not precised', () => {
    it('should not dispatch any event', () => {
      // given
      const fakeMatomoTracker = {
        push: jest.fn(),
      }
      // eslint-disable-next-line
      window._paq = fakeMatomoTracker
      const location = undefined

      // when
      shallow(
        <Matomo location={location}>
          <div>Children</div>
        </Matomo>
      )

      // then
      expect(fakeMatomoTracker.push).not.toHaveBeenCalled()
    })
  })
})

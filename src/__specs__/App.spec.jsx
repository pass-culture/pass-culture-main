import React from 'react'
import { mount, shallow } from 'enzyme/build'
import { App } from '../App'
import RedirectToMaintenance from '../components/RedirectToMaintenance'

describe('src | App', () => {
  it('should render children components', () => {
    // Given
    const props = { modalOpen: false, isMaintenanceActivated: false }

    // When
    const wrapper = mount(
      <App {...props}>
        <p>
          {'Sub component'}
        </p>
      </App>
    )

    // Then
    expect(wrapper.text()).toBe('Sub component')
  })

  it('should render an App component when isMaintenanceActivated is false', () => {
    // Given
    const props = { modalOpen: false, isMaintenanceActivated: false }

    // When
    const wrapper = mount(
      <App {...props}>
        <p>
          {'Sub component'}
        </p>
      </App>
    )

    // Then
    const appNode = wrapper.find(App)
    expect(appNode).toHaveLength(1)
    expect(appNode.text()).toBe('Sub component')
  })

  it('should render a Redirect component when isMaintenanceActivated is true', () => {
    // Given
    const props = { modalOpen: false, isMaintenanceActivated: true }

    // When
    const wrapper = shallow(
      <App {...props}>
        <p>
          {'Sub component'}
        </p>
      </App>
    )

    // Then
    const redirectNode = wrapper.find(RedirectToMaintenance)
    expect(redirectNode).toHaveLength(1)
  })
})

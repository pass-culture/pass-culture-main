import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { act, render, screen } from '@testing-library/react'

import FeaturedRoute from '../FeaturedRoute'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'

jest.mock('repository/pcapi/pcapi', () => ({
  loadFeatures: jest.fn(),
}))

const testActiveFeature = {
  description: 'Active testing feature',
  id: 'FAKEID',
  isActive: true,
  name: 'TEST_FEATURE',
  nameKey: 'TEST_FEATURE',
}

const testInactiveFeature = {
  description: 'Active testing feature',
  id: 'FAKEID',
  isActive: false,
  name: 'TEST_FEATURE',
  nameKey: 'TEST_FEATURE',
}

const Foo = () => <div>I’m foo component</div>

const renderFeatureRoute = async (props, store) => {
  const routePath = '/test/path'

  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: routePath }]}>
          <FeaturedRoute path={routePath} {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('src | components | router | FeaturedRoute', () => {
  let store

  beforeEach(() => {
    store = configureTestStore({ features: { initialized: false } })
    pcapi.loadFeatures.mockResolvedValue([])
  })

  describe('when features are not yet loaded', () => {
    beforeEach(async () => {
      // given
      pcapi.loadFeatures.mockImplementation(() => {
        return new Promise(resolve =>
          setTimeout(() => resolve([testActiveFeature]), 2000)
        )
      })

      const props = {
        component: Foo,
        featureName: 'TEST_FEATURE',
      }

      // when
      await renderFeatureRoute(props, store)
    })

    it('should render spinner instead of Foo component', async () => {
      // then
      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      expect(screen.queryByText('I’m foo component')).not.toBeInTheDocument()
    })

    it('should call requestGetFeatures', () => {
      // then
      expect(pcapi.loadFeatures).toHaveBeenCalledTimes(1)
    })
  })

  describe('when features are loaded and disabled', () => {
    beforeEach(async () => {
      // given
      store = configureTestStore({
        features: {
          initialized: true,
          list: [testInactiveFeature],
        },
      })

      const props = {
        component: Foo,
        featureName: 'TEST_FEATURE',
      }

      // when
      await renderFeatureRoute(props, store)
    })

    it('should render NotMatch instead of Foo component', () => {
      // then
      expect(screen.getByText('Cette page n’existe pas.')).toBeInTheDocument()
      expect(screen.queryByText('I’m foo component')).not.toBeInTheDocument()
    })

    it('should not call requestGetFeatures', () => {
      // then
      expect(pcapi.loadFeatures).toHaveBeenCalledTimes(0)
    })
  })

  describe('when features are loaded and not disabled', () => {
    beforeEach(async () => {
      // given
      store = configureTestStore({
        features: {
          initialized: true,
          list: [testActiveFeature],
        },
      })

      const props = {
        component: Foo,
        featureName: 'TEST_FEATURE',
      }

      // when
      await renderFeatureRoute(props, store)
    })

    it('should render Foo', () => {
      // then
      expect(screen.getByText('I’m foo component')).toBeInTheDocument()
    })

    it('should not call requestGetFeatures', () => {
      // then
      expect(pcapi.loadFeatures).toHaveBeenCalledTimes(0)
    })
  })
})

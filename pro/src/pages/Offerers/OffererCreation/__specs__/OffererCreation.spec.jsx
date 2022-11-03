import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import OffererCreation from '../OffererCreation'

const renderOffererCreation = store => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <OffererCreation />
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | OffererCreation', () => {
  describe('render', () => {
    it('should render a OffererCreationUnavailable component when pro offerer creation is disabled', () => {
      const store = configureTestStore({
        features: {
          initialized: true,
          list: [
            {
              description: 'Active feature',
              id: 'DISABLE_ENTERPRISE_API',
              isActive: true,
              name: 'DISABLE_ENTERPRISE_API',
              nameKey: 'DISABLE_ENTERPRISE_API',
            },
          ],
        },
      })

      renderOffererCreation(store)

      expect(
        screen.getByText('Impossibilité de créer une structure actuellement.')
      ).toBeInTheDocument()
    })

    it('should render a OffererCreation component', () => {
      const store = configureTestStore({})

      renderOffererCreation(store)

      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })
})

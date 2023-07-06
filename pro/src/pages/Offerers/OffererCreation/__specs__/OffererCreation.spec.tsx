import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import OffererCreation from '../OffererCreation'

const renderOffererCreation = (storeOverrides: any) =>
  renderWithProviders(<OffererCreation />, { storeOverrides })

describe('src | components | OffererCreation', () => {
  describe('render', () => {
    it('should render a OffererCreationUnavailable component when pro offerer creation is disabled', () => {
      const store = {
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
      }

      renderOffererCreation(store)

      expect(
        screen.getByText('Impossibilité de créer une structure actuellement.')
      ).toBeInTheDocument()
    })

    it('should render a OffererCreation component', () => {
      const store = {}

      renderOffererCreation(store)

      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })
})

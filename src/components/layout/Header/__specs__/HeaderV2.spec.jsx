import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import HeaderV2 from '../HeaderV2'

const renderHeader = props => {
  const stubStore = configureTestStore()

  return render(
    <Provider store={stubStore}>
      <MemoryRouter>
        <HeaderV2 {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('navigation menu', () => {
  it('should have link to Styleguide when is enabled', () => {
    // When
    renderHeader({ isStyleguideActive: true })

    // Then
    expect(screen.queryByTestId('styleguide')).toBeInTheDocument()
  })

  it('should not have link to Styleguide when is disabled', () => {
    // When
    renderHeader({ isStyleguideActive: false })

    // Then
    expect(screen.queryByTestId('styleguide')).not.toBeInTheDocument()
  })

  describe('when clicking on Home icon', () => {
    it('should redirect to /accueil when user is not admin', () => {
      // When
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // Then
      expect(screen.getByText('Accueil').closest('a')).toHaveAttribute('href', '/accueil')
    })

    it('should redirect to /structures when user is admin', () => {
      // When
      renderHeader({ isUserAdmin: true, isStyleguideActive: false })

      // Then
      expect(screen.getByText('Accueil').closest('a')).toHaveAttribute('href', '/structures')
    })
  })
})

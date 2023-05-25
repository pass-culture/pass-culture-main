import { screen } from '@testing-library/react'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'

import { defaultAlgoliaHits } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { ResultType } from 'utils/types'

import { AdageHeaderComponent } from '../AdageHeader'

const renderAdageHeader = (hits: Hit<ResultType>[] = []) => {
  renderWithProviders(<AdageHeaderComponent hits={hits} />)
}

describe('AdageHeader', () => {
  it('should render adage header', () => {
    renderAdageHeader()

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement 0' })
    ).toBeInTheDocument()
    expect(screen.getByText('Suivi')).toBeInTheDocument()
  })

  it('should render the number of hits', () => {
    renderAdageHeader([defaultAlgoliaHits, defaultAlgoliaHits])

    expect(screen.getByText('2')).toBeInTheDocument()
  })
})

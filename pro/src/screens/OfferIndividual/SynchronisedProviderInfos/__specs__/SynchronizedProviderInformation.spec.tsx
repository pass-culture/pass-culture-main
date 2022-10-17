import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import SynchronizedProviderInformation, {
  ISynchronizedProviderInformation,
} from '../SynchronizedProviderInformation'

const renderSynchronizedProviderInformation = ({
  props,
}: {
  props: ISynchronizedProviderInformation
}) => {
  return render(<SynchronizedProviderInformation {...props} />)
}

describe('SynchronizedProviderInformation', () => {
  it('should not render when provider does not exist', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'unknown provider id' },
    })
    expect(
      screen.queryByTestId('synchronized-provider-information')
    ).not.toBeInTheDocument()
  })

  it('should render for provider "leslibraires.fr"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'leslibraires.fr' },
    })
    expect(
      screen.getByText('Offre synchronisée avec Leslibraires.fr')
    ).toBeInTheDocument()
  })

  it('should render for provider "allociné"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'allociné' },
    })
    expect(
      screen.getByText('Offre synchronisée avec Allociné')
    ).toBeInTheDocument()
  })
})

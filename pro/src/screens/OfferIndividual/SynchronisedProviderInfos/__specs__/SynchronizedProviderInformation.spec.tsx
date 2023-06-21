import { render, screen } from '@testing-library/react'
import React from 'react'

import SynchronizedProviderInformation, {
  SynchronizedProviderInformationProps,
} from '../SynchronizedProviderInformation'

const renderSynchronizedProviderInformation = ({
  props,
}: {
  props: SynchronizedProviderInformationProps
}) => {
  return render(<SynchronizedProviderInformation {...props} />)
}

describe('SynchronizedProviderInformation', () => {
  it('should not render when provider does not exist', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'unknown provider id' },
    })
    expect(
      screen.queryByText('Offre synchronisée', { exact: false })
    ).not.toBeInTheDocument()
  })

  it('should render for provider "leslibraires.fr"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'leslibraires.fr' },
    })
    expect(
      screen.getByText('Offre synchronisée avec Leslibraires.fr')
    ).toBeInTheDocument()
    expect(screen.queryByText('À SAVOIR')).not.toBeInTheDocument()
  })

  it('should render for provider "allociné"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'allociné' },
    })
    expect(
      screen.getByText('Offre synchronisée avec Allociné')
    ).toBeInTheDocument()
    expect(screen.queryByText('À SAVOIR')).not.toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  SynchronizedProviderInformation,
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
  it('should render a default message provider is not from known list', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'unknown provider id' },
    })
    expect(
      screen.queryByText('unknown provider id', { exact: false })
    ).toBeInTheDocument()
  })

  it('should render for provider "leslibraires.fr"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'leslibraires.fr' },
    })
    expect(
      screen.getByText('Offre synchronisée avec leslibraires.fr')
    ).toBeInTheDocument()
    expect(screen.queryByText('À SAVOIR')).not.toBeInTheDocument()
  })

  it('should render for provider "allociné"', () => {
    renderSynchronizedProviderInformation({
      props: { providerName: 'allociné' },
    })
    expect(
      screen.getByText('Offre synchronisée avec allociné')
    ).toBeInTheDocument()
    expect(screen.queryByText('À SAVOIR')).not.toBeInTheDocument()
  })
})

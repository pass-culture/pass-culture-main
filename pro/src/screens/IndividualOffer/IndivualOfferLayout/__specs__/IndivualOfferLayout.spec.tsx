import { screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndivualOfferLayout,
  IndivualOfferLayoutProps,
} from '../IndivualOfferLayout'

const renderIndivualOfferLayout = ({
  title = 'layout title',
  withStepper = true,
  offer = getIndividualOfferFactory(),
  mode = OFFER_WIZARD_MODE.EDITION,
  children = <div>Template child</div>,
}: Partial<IndivualOfferLayoutProps>) => {
  renderWithProviders(
    <IndivualOfferLayout
      title={title}
      withStepper={withStepper}
      offer={offer}
      mode={mode}
    >
      {children}
    </IndivualOfferLayout>
  )
}

describe('IndivualOfferLayout', () => {
  it('should render when no offer is given', () => {
    renderIndivualOfferLayout({ offer: null })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
  })

  it('should render when offer is given', () => {
    const offer = getIndividualOfferFactory({
      name: 'offer name',
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()

    expect(screen.getByText(/offer name/)).toBeInTheDocument()
    expect(screen.getByText(/layout title/)).toBeInTheDocument()
  })

  it('should not display stepper nor status when no stepper', () => {
    const offer = getIndividualOfferFactory({
      isActive: true,
      status: OfferStatus.ACTIVE,
    })

    renderIndivualOfferLayout({
      offer,
      withStepper: false,
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
    expect(screen.queryByText('Détails de l’offre')).not.toBeInTheDocument()
    expect(screen.queryByText('Stock & Prix')).not.toBeInTheDocument()
  })

  it('should display status and button in edition', () => {
    const offer = getIndividualOfferFactory({
      isActive: true,
      status: OfferStatus.ACTIVE,
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(screen.getByText('Désactiver')).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display status but not let activate offer when offer is not activable', () => {
    const offer = getIndividualOfferFactory({
      isActivable: false,
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Désactiver' })
    ).not.toBeInTheDocument()
  })

  it('should not display status in creation', () => {
    const offer = getIndividualOfferFactory({
      isActive: false,
      status: OfferStatus.DRAFT,
    })

    renderIndivualOfferLayout({
      offer,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Désactiver' })
    ).not.toBeInTheDocument()
  })

  it('should display provider banner', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'boost' },
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(
      screen.getByText('Offre synchronisée avec Boost')
    ).toBeInTheDocument()
  })

  it('should not display provider banner when no provider is provided', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: '' },
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.queryByText('Offre synchronisée')).not.toBeInTheDocument()
  })
})

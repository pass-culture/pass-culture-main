import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { OFFER_WIZARD_MODE } from 'core/Offers'
import { configureTestStore } from 'store/testUtils'

import { BannerSummary } from '../'

describe('components:BannerSummary', () => {
  it('renders component successfully when offer is not draft', async () => {
    render(
      <Provider store={configureTestStore()}>
        <BannerSummary mode={OFFER_WIZARD_MODE.CREATION} />
      </Provider>
    )
    expect(
      screen.getByText(
        /Vérifiez les informations ci-dessous avant de publier votre offre./
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres./
      )
    ).toBeInTheDocument()
  })
  it('renders component successfully when offer is draft', async () => {
    render(
      <Provider store={configureTestStore()}>
        <BannerSummary mode={OFFER_WIZARD_MODE.DRAFT} />
      </Provider>
    )
    expect(
      screen.getByText(
        /Vérifiez les informations ci-dessous avant de publier votre offre./
      )
    ).toBeInTheDocument()
    expect(
      await screen.queryByText(
        /Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres./
      )
    ).not.toBeInTheDocument()
  })
})

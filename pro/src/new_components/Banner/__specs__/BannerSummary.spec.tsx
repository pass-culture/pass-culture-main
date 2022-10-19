// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import { BannerSummary } from '../'

describe('new_components:BannerSummary', () => {
  it('renders component successfully', async () => {
    const store = {
      features: {
        list: [{ isActive: false, nameKey: 'OFFER_DRAFT_ENABLED' }],
      },
    }

    render(
      <Provider store={configureTestStore(store)}>
        <BannerSummary />
      </Provider>
    )

    expect(
      screen.getByText(
        'Vérifiez les informations ci-dessous avant de publier votre offre.'
      )
    ).toBeInTheDocument()
  })
  it('renders component successfully when draft offers are enabled', async () => {
    const store = {
      features: {
        list: [{ isActive: true, nameKey: 'OFFER_DRAFT_ENABLED' }],
      },
    }
    render(
      <Provider store={configureTestStore(store)}>
        <BannerSummary />
      </Provider>
    )
    expect(
      screen.getByText(
        'Vérifiez les informations ci-dessous avant de publier votre offre. Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres.'
      )
    ).toBeInTheDocument()
  })
})

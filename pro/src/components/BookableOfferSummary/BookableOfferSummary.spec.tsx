import { screen } from '@testing-library/react'

import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { BookableOfferSummary, BookableOfferSummaryProps } from './BookableOfferSummary'

describe('CollectiveStatusLabel', () => {
  let props: BookableOfferSummaryProps
  beforeEach(() => {
    const offer = getCollectiveOfferFactory()
    props = {
      offer,
    }
  })

  it(
    'should render',
    () => {

      renderWithProviders(
        <BookableOfferSummary {...props} />
      )
      expect(screen.getByText('Nouveau composant de recap pour une offre réservable : Work in progress')).toBeInTheDocument()
    }
  )
})

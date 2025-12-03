import { screen } from '@testing-library/react'

import { CollectiveOfferTypeEnum } from '@/commons/core/Offers/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { TemplateOffersSearchFilters } from './TemplateOffersSearchFilters'

describe('TemplateOffersSearchFilters', () => {
  it('should render filters correctly', () => {
    renderWithProviders(
      <TemplateOffersSearchFilters
        hasFilters={false}
        applyFilters={() => vi.fn()}
        setSelectedFilters={() => vi.fn()}
        disableAllFilters={false}
        resetFilters={() => vi.fn()}
        offererId={undefined}
        selectedFilters={{
          name: '',
          offererId: '',
          venueId: '',
          format: 'all',
          status: [],
          collectiveOfferType: CollectiveOfferTypeEnum.TEMPLATE,
          periodBeginningDate: '',
          periodEndingDate: '',
          locationType: undefined,
          offererAddressId: undefined,
          page: undefined,
        }}
      />
    )
    expect(screen.getByLabelText('Nom de l’offre')).toBeInTheDocument()
    expect(screen.getByLabelText('Statut')).toBeInTheDocument()
    expect(screen.getByLabelText('Format')).toBeInTheDocument()
    expect(screen.getByText('Période de l’évènement')).toBeInTheDocument()
  })
})

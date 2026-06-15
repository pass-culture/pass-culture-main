import { render, screen } from '@testing-library/react'

import { OpeningHoursRow } from '../OpeningHoursRow'

describe('OpeningHoursRow', () => {
  it('should render nothing when the day is null', () => {
    const { container } = render(<OpeningHoursRow openingHoursForDay={null} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('should render nothing when the day has no timespan', () => {
    const { container } = render(<OpeningHoursRow openingHoursForDay={[]} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('should render a single timespan', () => {
    const { container } = render(
      <OpeningHoursRow openingHoursForDay={[['09:00', '12:00']]} />
    )

    expect(container).toHaveTextContent('09:00-12:00')
    expect(screen.queryByText(/et/)).not.toBeInTheDocument()
  })

  it('should render two timespans separated by "et"', () => {
    const { container } = render(
      <OpeningHoursRow
        openingHoursForDay={[
          ['09:00', '12:00'],
          ['14:00', '18:00'],
        ]}
      />
    )

    expect(container).toHaveTextContent('09:00-12:00 et 14:00-18:00')
  })
})

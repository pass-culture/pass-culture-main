import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useIsElementVisible from '@/commons/hooks/useIsElementVisible'

import { Carousel } from '../Carousel'

vi.mock('@/commons/hooks/useIsElementVisible', () => ({
  useIsElementVisible: vi.fn(() => [false, false]),
}))

const mockCarouselElements = Array(20)
  .fill(null)
  .map((_el, i) => <div key={i}>Element {i}</div>)

describe('Carousel', () => {
  it('should display the list of elements in the carousel', () => {
    render(<Carousel elements={mockCarouselElements} />)

    expect(screen.getByText('Element 1')).toBeInTheDocument()
    expect(screen.getByText('Element 15')).toBeInTheDocument()
  })

  it('should display the title of the list if it exists', () => {
    render(
      <Carousel
        elements={mockCarouselElements}
        title={<h1>Carousel title</h1>}
      />
    )

    expect(
      screen.getByRole('heading', { name: 'Carousel title' })
    ).toBeInTheDocument()
  })

  it('should have the left or right arrow enabled when respectively the first or last element is not fully visible', () => {
    render(<Carousel elements={mockCarouselElements} />)

    expect(screen.getByTestId('carousel-arrow-left')).not.toBeDisabled()
    expect(screen.getByTestId('carousel-arrow-right')).not.toBeDisabled()
  })

  it('should have the left or right arrow disabled when respectively the first or last element is visible', () => {
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true,
      false,
    ])
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true,
      false,
    ])

    render(<Carousel elements={mockCarouselElements} />)

    expect(screen.getByTestId('carousel-arrow-left')).toBeDisabled()
    expect(screen.getByTestId('carousel-arrow-right')).toBeDisabled()
  })

  it('should modify the list horizontal scroll when the arrows are clicked', async () => {
    render(<Carousel elements={mockCarouselElements} />)

    expect(screen.getByRole('list').scrollLeft).toEqual(0)
    await userEvent.click(screen.getByTestId('carousel-arrow-right'))
    expect(screen.getByRole('list').scrollLeft).toEqual(400)
    await userEvent.click(screen.getByTestId('carousel-arrow-left'))
    expect(screen.getByRole('list').scrollLeft).toEqual(0)
  })

  it('should emit an event when the last element is seen entirely', () => {
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true, // first element visible
    ])
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true, // last element visible
      true, // last element changed
    ])

    const mockEmittedEnvent = vi.fn()
    render(
      <Carousel
        elements={mockCarouselElements}
        onLastCarouselElementVisible={mockEmittedEnvent}
      />
    )

    expect(mockEmittedEnvent).toHaveBeenCalledOnce()
  })

  it('should not emit an event when the last element seen has not changed', () => {
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true, // first element visible
    ])
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockReturnValueOnce([
      true, // last element visible
      false, // last element did not change
    ])

    const mockEmittedEnvent = vi.fn()
    render(
      <Carousel
        elements={mockCarouselElements}
        onLastCarouselElementVisible={mockEmittedEnvent}
      />
    )

    expect(mockEmittedEnvent).not.toHaveBeenCalled()
  })
})

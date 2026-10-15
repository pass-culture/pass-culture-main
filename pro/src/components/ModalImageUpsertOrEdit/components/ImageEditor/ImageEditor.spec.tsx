import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import { ImageEditor, map } from './ImageEditor'

vi.mock('use-debounce', async () => ({
  ...(await vi.importActual('use-debounce')),
  useDebouncedCallback: vi.fn((fn) => fn),
}))

describe('ImageEditor', () => {
  const mockImage = new File(['image'], 'image.jpg', { type: 'image/jpeg' })
  const initialInnerWidth = global.innerWidth

  afterEach(() => {
    global.innerWidth = initialInnerWidth
  })

  const defaultProps = {
    image: mockImage,
    canvasHeight: 500,
    canvasWidth: 500,
    cropBorderColor: 'red',
    cropBorderHeight: 20,
    cropBorderWidth: 20,
    maxScale: 4,
  }

  const CANVAS_LABEL = "Editeur de cadrage et de zoom de l'image"

  it('renders correctly', () => {
    render(<ImageEditor {...defaultProps} />)

    expect(
      screen.getByRole('application', { name: CANVAS_LABEL })
    ).toHaveProperty('tagName', 'CANVAS')
    expect(screen.getByTestId('slider')).toBeInTheDocument()
  })

  describe('with a loaded image', () => {
    // jsdom never loads images: fire the load event as soon as the source is set.
    function createLoadedImage() {
      const image = document.createElement('img')
      image.width = 1200
      image.height = 800
      Object.defineProperty(image, 'src', {
        set: () => setTimeout(() => image.dispatchEvent(new Event('load'))),
      })
      return image
    }

    beforeEach(() => {
      vi.spyOn(window, 'Image').mockImplementation(createLoadedImage)
    })

    const renderLoadedImageEditor = async (
      props: Partial<typeof defaultProps> & { onChangeDone?: () => void } = {}
    ) => {
      const view = render(<ImageEditor {...defaultProps} {...props} />)
      await waitFor(() =>
        expect(screen.getByRole('status')).not.toBeEmptyDOMElement()
      )
      return view
    }

    // A 1200x800 image in a square crop area: 2/3 of its width are visible
    const INITIAL_EDITOR_STATE =
      'Zoom : 100 %. Zone cadrée : de 17 à 83 % de la largeur et de 0 à 100 % de la hauteur de l’image.'

    it('should describe the zoom and the cropped area to assistive technologies', async () => {
      const { container } = await renderLoadedImageEditor()

      const canvas = screen.getByLabelText(CANVAS_LABEL)
      expect(canvas).toHaveAttribute('tabindex', '0')
      expect(canvas).toHaveAttribute('aria-roledescription', 'éditeur d’image')
      expect(screen.getByRole('status')).toHaveTextContent(INITIAL_EDITOR_STATE)
      expect(canvas).toHaveAccessibleDescription(
        `${INITIAL_EDITOR_STATE} Utilisez les flèches du clavier pour déplacer l’image et les touches + et - pour zoomer.`
      )
      expect(await axe(container)).toHaveNoViolations()
    })

    it('should not mention keyboard zoom when zoom is disabled', async () => {
      await renderLoadedImageEditor({ maxScale: 1 })

      expect(screen.getByLabelText(CANVAS_LABEL)).toHaveAccessibleDescription(
        `${INITIAL_EDITOR_STATE} Utilisez les flèches du clavier pour déplacer l’image.`
      )
    })

    it('should move the cropped area with the keyboard arrows', async () => {
      const onChangeDone = vi.fn()
      await renderLoadedImageEditor({ onChangeDone })

      await userEvent.tab()
      expect(screen.getByLabelText(CANVAS_LABEL)).toHaveFocus()

      await userEvent.keyboard('{Shift>}{ArrowRight}{/Shift}')

      await waitFor(() =>
        expect(screen.getByRole('status')).toHaveTextContent(
          'Zoom : 100 %. Zone cadrée : de 10 à 77 % de la largeur et de 0 à 100 % de la hauteur de l’image.'
        )
      )
      expect(onChangeDone).toHaveBeenCalled()
    })

    it('should zoom in and out with the keyboard "+" and "-" keys', async () => {
      const onChangeDone = vi.fn()
      await renderLoadedImageEditor({ onChangeDone })

      await userEvent.tab()
      await userEvent.keyboard('+')

      expect(screen.getByText('Zoom : 110 %')).toBeInTheDocument()
      await waitFor(() =>
        expect(screen.getByRole('status')).toHaveTextContent(
          'Zoom : 110 %. Zone cadrée : de 20 à 80 % de la largeur et de 5 à 95 % de la hauteur de l’image.'
        )
      )
      expect(onChangeDone).toHaveBeenCalled()

      await userEvent.keyboard('-')

      expect(screen.getByText('Zoom : 100 %')).toBeInTheDocument()
    })

    it('should not zoom out below 100 % with the keyboard', async () => {
      await renderLoadedImageEditor()

      await userEvent.tab()
      await userEvent.keyboard('-')

      expect(screen.getByText('Zoom : 100 %')).toBeInTheDocument()
    })

    it('should not zoom with the keyboard when zoom is disabled', async () => {
      await renderLoadedImageEditor({ maxScale: 1 })

      await userEvent.tab()
      await userEvent.keyboard('+')

      expect(screen.getByText('Zoom : 100 %')).toBeInTheDocument()
    })
  })

  it('handles window resize and adjusts canvas size', () => {
    render(<ImageEditor {...defaultProps} />)

    expect(screen.getByLabelText(CANVAS_LABEL)).toHaveAttribute('width', '540')
    expect(screen.getByLabelText(CANVAS_LABEL)).toHaveAttribute('height', '540')
  })

  it('handles zoom slider change correctly', () => {
    render(<ImageEditor {...defaultProps} />)

    const slider = screen.getByTestId('slider')
    fireEvent.change(slider, { target: { value: 2 } })

    expect(slider).toHaveValue('2')
  })

  it('calls onChangeDone when the image is changed via slider', () => {
    const onChangeDone = vi.fn()
    render(<ImageEditor {...defaultProps} onChangeDone={onChangeDone} />)

    const slider = screen.getByTestId('slider')
    fireEvent.change(slider, { target: { value: 2 } })

    expect(onChangeDone).toHaveBeenCalled()
  })

  it('displays a warning when scale is disabled', () => {
    render(<ImageEditor {...defaultProps} initialScale={0} maxScale={1} />)

    expect(
      screen.getByText('L’image est trop petite pour utiliser le zoom.')
    ).toBeInTheDocument()
  })

  it.each([
    { name: 'portrait', canvasHeight: 297, canvasWidth: 198, ratio: 2 / 3 },
    { name: 'landscape', canvasHeight: 138, canvasWidth: 207, ratio: 3 / 2 },
  ])(
    'keeps the $name canvas ratio when it is shrunk on a mobile screen',
    ({ canvasHeight, canvasWidth, ratio }) => {
      // Mobile screen width in the sentry issue : https://pass-culture.sentry.io/issues/127987982
      global.innerWidth = 384

      // No crop border, so that the canvas dimensions are the crop area ones
      render(
        <ImageEditor
          {...defaultProps}
          canvasHeight={canvasHeight}
          canvasWidth={canvasWidth}
          cropBorderHeight={0}
          cropBorderWidth={0}
        />
      )

      const canvas = screen.getByLabelText(CANVAS_LABEL)
      const width = Number(canvas.getAttribute('width'))
      const height = Number(canvas.getAttribute('height'))

      expect(width / height).toBeCloseTo(ratio)
    }
  )
})

describe('ImageEditor:map', () => {
  it('maps values correctly', () => {
    const result = map(5, 0, 10, 0, 100)
    expect(result).toBe(50)
  })

  it('clamps values correctly when above max', () => {
    const result = map(15, 0, 10, 0, 100)
    expect(result).toBe(100)
  })

  it('clamps values correctly when below min', () => {
    const result = map(-5, 0, 10, 0, 100)
    expect(result).toBe(0)
  })
})

import { render, screen } from '@testing-library/react'
import { createRef } from 'react'
import { axe } from 'vitest-axe'

import { BaseDialog } from './BaseDialog'

describe('<BaseDialog />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <BaseDialog isOpen onClose={() => {}} ariaLabelledBy="title">
        <h2 id="title">Title</h2>
      </BaseDialog>
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should focus refToFocusOnClose when the dialog closes', () => {
    const refToFocusOnClose = createRef<HTMLButtonElement>()
    const { rerender } = render(
      <>
        <button ref={refToFocusOnClose} type="button">
          Outside
        </button>
        <BaseDialog
          isOpen
          onClose={() => {}}
          ariaLabelledBy="title"
          refToFocusOnClose={refToFocusOnClose}
        >
          <h2 id="title">Title</h2>
        </BaseDialog>
      </>
    )

    rerender(
      <>
        <button ref={refToFocusOnClose} type="button">
          Outside
        </button>
        <BaseDialog
          isOpen={false}
          onClose={() => {}}
          ariaLabelledBy="title"
          refToFocusOnClose={refToFocusOnClose}
        >
          <h2 id="title">Title</h2>
        </BaseDialog>
      </>
    )

    expect(screen.getByRole('button', { name: 'Outside' })).toHaveFocus()
  })
})

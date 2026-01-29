import * as Dialog from '@radix-ui/react-dialog'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createRef, type LegacyRef } from 'react'
import { axe } from 'vitest-axe'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import { DialogBuilder, type DialogBuilderProps } from './DialogBuilder'

const defaultProps: DialogBuilderProps = {
  children: (
    <>
      <p>Dialog content</p>
      <DialogBuilder.Footer>
        <div>
          <Dialog.Close asChild>
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              label="Annuler"
            />
          </Dialog.Close>
          <Dialog.Close asChild>
            <Button label="Continuer" />
          </Dialog.Close>
        </div>
      </DialogBuilder.Footer>
    </>
  ),
  title: 'Dialog title',
  trigger: <Button label="Open the dialog" />,
}

function renderDialogBuilder(
  props: Partial<DialogBuilderProps> = {},
  externalFocusRef?: LegacyRef<HTMLButtonElement>
) {
  const mergedProps = { ...defaultProps, ...props }

  return render(
    <>
      {externalFocusRef && (
        <button ref={externalFocusRef} type="button">
          External button
        </button>
      )}
      <DialogBuilder {...mergedProps}>{mergedProps.children}</DialogBuilder>
    </>
  )
}

describe('DialogBuilder', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderDialogBuilder()

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should open a dialog with a title and a footer', async () => {
    renderDialogBuilder()

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )
    expect(screen.getByRole('heading', { name: 'Dialog title' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Continuer' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Annuler' })).toBeVisible()
    expect(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    ).toBeVisible()
  })

  it('should close the dialog when clicking the close button', async () => {
    renderDialogBuilder()

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    )
    expect(
      screen.queryByRole('heading', { name: 'Dialog title' })
    ).not.toBeInTheDocument()
  })

  it('should close the dialog when clicking outside the dialog', async () => {
    renderDialogBuilder()

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    await userEvent.click(screen.getByTestId('dialog-overlay'))
    expect(
      screen.queryByRole('heading', { name: 'Dialog title' })
    ).not.toBeInTheDocument()
  })

  it('should render dialog open by default when defaultOpen is true', () => {
    renderDialogBuilder({ defaultOpen: true })

    expect(screen.getByRole('heading', { name: 'Dialog title' })).toBeVisible()
  })

  it('should render dialog without trigger when trigger prop is not provided', () => {
    renderDialogBuilder({ trigger: undefined, defaultOpen: true })

    expect(
      screen.queryByRole('button', { name: 'Open the dialog' })
    ).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Dialog title' })).toBeVisible()
  })

  it('should call onOpenChange callback when dialog state changes', async () => {
    const onOpenChange = vi.fn()
    renderDialogBuilder({ onOpenChange })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )
    expect(onOpenChange).toHaveBeenCalledWith(true)

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    )
    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('should control dialog state with open prop', () => {
    const { rerender } = render(
      <DialogBuilder {...defaultProps} open={false}>
        {defaultProps.children}
      </DialogBuilder>
    )

    expect(
      screen.queryByRole('heading', { name: 'Dialog title' })
    ).not.toBeInTheDocument()

    rerender(
      <DialogBuilder {...defaultProps} open={true}>
        {defaultProps.children}
      </DialogBuilder>
    )

    expect(screen.getByRole('heading', { name: 'Dialog title' })).toBeVisible()
  })

  it('should render with visually hidden title when isTitleHidden is true', async () => {
    renderDialogBuilder({ isTitleHidden: true })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    const dialog = screen.getByRole('dialog')
    const title = within(dialog).getByRole('heading', { name: 'Dialog title' })
    expect(title).toBeInTheDocument()
  })

  it('should render imageTitle alongside the title', async () => {
    const imageTitle = <img src="test.png" alt="Test image" />
    renderDialogBuilder({ imageTitle })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    expect(screen.getByRole('img', { name: 'Test image' })).toBeVisible()
  })

  it('should render imageTitle without title text when only imageTitle is provided', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const imageTitle = <img src="test.png" alt="Test image title" />
    renderDialogBuilder({ title: undefined, imageTitle })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
    vi.restoreAllMocks()
  })

  it('should apply custom className to dialog content', async () => {
    renderDialogBuilder({ className: 'custom-dialog-class' })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toBeVisible()
    expect(dialog).toHaveClass('custom-dialog-class')
  })

  it('should apply drawer variant styles when variant is drawer', async () => {
    renderDialogBuilder({ variant: 'drawer' })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    const overlay = screen.getByTestId('dialog-overlay')
    expect(overlay).toBeVisible()
    expect(overlay).toHaveClass('dialog-builder-overlay-drawer')
  })

  it('should focus external element on close when refToFocusOnClose is provided', async () => {
    const externalFocusRef = createRef<HTMLButtonElement>()
    renderDialogBuilder(
      { refToFocusOnClose: externalFocusRef },
      externalFocusRef
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    )

    expect(
      screen.getByRole('button', { name: 'External button' })
    ).toHaveFocus()
  })
})

describe('DialogBuilder.Footer', () => {
  it('should render footer with custom className', async () => {
    renderDialogBuilder({
      children: (
        <DialogBuilder.Footer className="custom-footer-class">
          <button type="button">Footer button</button>
        </DialogBuilder.Footer>
      ),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )

    const footerButton = screen.getByRole('button', { name: 'Footer button' })
    expect(footerButton).toBeVisible()
    expect(footerButton.parentElement).toHaveClass('custom-footer-class')
  })
})

import * as Dialog from '@radix-ui/react-dialog'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { DialogBuilder, DialogBuilderProps } from './DialogBuilder'

const defaultProps: DialogBuilderProps = {
  children: (
    <>
      <p>Dialog content</p>
      <DialogBuilder.Footer>
        <div>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Dialog.Close asChild>
            <Button>Continuer</Button>
          </Dialog.Close>
        </div>
      </DialogBuilder.Footer>
    </>
  ),
  title: 'Dialog title',
  trigger: <Button>Open the dialog</Button>,
}

function renderDialogBuilder(props = defaultProps) {
  return render(<DialogBuilder {...props}>{props.children}</DialogBuilder>)
}

describe('DialogBuilder', () => {
  it('should open a dialog with a title and a footer', async () => {
    renderDialogBuilder()

    await userEvent.click(
      screen.getByRole('button', { name: 'Open the dialog' })
    )
    expect(
      screen.getByRole('heading', { name: 'Dialog title' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    ).toBeInTheDocument()
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
})

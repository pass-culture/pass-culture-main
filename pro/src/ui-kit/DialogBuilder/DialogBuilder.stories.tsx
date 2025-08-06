import * as Dialog from '@radix-ui/react-dialog'
import type { StoryObj } from '@storybook/react'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { DialogBuilder } from './DialogBuilder'

export default {
  title: '@/ui-kit/DialogBuilder',
  component: DialogBuilder,
}

export const Default: StoryObj<typeof DialogBuilder> = {
  args: {
    trigger: <Button>Cliquez ici!</Button>,
    children: (
      <>
        <Dialog.Title asChild>
          <h1>Dialog title</h1>
        </Dialog.Title>
        <p>lorem ipsum dolor sit amet</p>
      </>
    ),
  },
}

export const Drawer: StoryObj<typeof DialogBuilder> = {
  args: {
    variant: 'drawer',
    trigger: <Button>Cliquez ici!</Button>,
    title: 'Dialog title',
    children: (
      <>
        <p>lorem ipsum dolor sit amet</p>
        <DialogBuilder.Footer>
          <div style={{ display: 'flex', gap: '24px' }}>
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
  },
}

export const DrawerWithLongContent: StoryObj<typeof DialogBuilder> = {
  args: {
    variant: 'drawer',
    trigger: <Button>Cliquez ici!</Button>,
    title: 'Dialog title',
    children: (
      <>
        <div style={{ padding: '1rem 0' }}>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
            blandit blandit purus, at suscipit arcu euismod lacinia. Suspendisse
            sed porttitor arcu, nec consequat sem. Integer eget tincidunt lacus.
            Nam luctus varius est a aliquam. Maecenas congue turpis a libero
            pellentesque commodo a in nulla. Aliquam erat volutpat. Morbi non
            arcu elit. Maecenas dictum at nunc nec dapibus. Donec sollicitudin
            nisi sed cursus lobortis. Ut arcu odio, varius at elit a,
            pellentesque scelerisque elit. Suspendisse potenti. Nullam malesuada
            dolor non iaculis euismod. Praesent vel enim ac eros consectetur
            tempus. Donec eget nibh nisl.
          </p>
          <p>
            Praesent tempor elementum enim vitae dapibus. Nunc consectetur
            finibus orci, vel venenatis nisi commodo lacinia. Donec suscipit
            nibh non pharetra porttitor. In nec arcu ultrices, consequat ex vel,
            scelerisque eros. Integer porttitor ipsum et urna suscipit, vel
            hendrerit orci lacinia. In ut facilisis tortor. Suspendisse luctus
            neque a odio vulputate malesuada ut sit amet nulla. Nam nec ipsum
            non mauris mollis rutrum. Phasellus vel sem volutpat, pellentesque
            augue ut, rhoncus eros. Quisque eu tellus ac lorem ornare iaculis.
          </p>
          <p>
            Morbi accumsan maximus justo, eu varius nunc posuere a. Fusce sed
            lacus a neque rutrum laoreet. Fusce varius bibendum interdum. Nunc
            consequat ex ac nisi porta ultricies. Curabitur sodales cursus
            purus, id efficitur orci condimentum eget. Etiam luctus massa id
            velit volutpat tincidunt. Ut at risus arcu. Nunc semper lacus in sem
            rhoncus elementum. Cras imperdiet vitae magna scelerisque ornare.
            Nam nec cursus urna.
          </p>
          <p>
            Aliquam dictum luctus lectus ac dignissim. Cras elementum interdum
            scelerisque. Cras consectetur purus ex, vel rutrum ante tincidunt
            non. Sed sapien purus, dignissim non odio sed, efficitur convallis
            libero. Proin tristique tellus fermentum nisl posuere, sed accumsan
            dui vulputate. Curabitur consequat rhoncus lacus sit amet consequat.
            Aliquam maximus, massa quis auctor lacinia, ipsum magna finibus
            quam, id hendrerit tortor tortor sit amet tortor. Mauris sit amet
            scelerisque dolor. Nulla facilisi. Cras a sapien vitae dolor euismod
            posuere in ut sem. Suspendisse vel nibh tortor. Quisque tempus a ex
            vitae auctor. Donec in viverra leo. Nam eu gravida quam, et feugiat
            metus. Proin egestas ipsum eget augue porttitor lobortis. Donec
            vitae quam dui.
          </p>
        </div>
        <DialogBuilder.Footer>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
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
  },
}

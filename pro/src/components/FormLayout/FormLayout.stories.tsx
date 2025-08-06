import type { StoryObj } from '@storybook/react'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import { FormLayout, FormLayoutProps } from './FormLayout'

export default {
  title: '@/components/FormLayout',
  component: FormLayout,
}

const DefaultFormLayout = (args: FormLayoutProps) => {
  return (
    <div style={{ width: 780 }}>
      <FormLayout {...args}>
        <FormLayout.Section
          description="Lorem ipsum dolor sit amet"
          title="Lorem ipsum dolor sit amet"
        >
          <FormLayout.Row>
            <label>
              Hello
              <input type="text" />
            </label>
          </FormLayout.Row>
        </FormLayout.Section>
        <FormLayout.Section
          description="Lorem ipsum dolor sit amet"
          title="Lorem ipsum dolor sit amet"
        >
          <FormLayout.Row>
            <label>
              Hello
              <input type="text" />
            </label>
          </FormLayout.Row>
          <FormLayout.SubSection title="Sub section title">
            <FormLayout.Row inline>
              <label>
                Hello
                <input type="text" />
              </label>
              <label>
                Hello
                <input type="text" />
              </label>
            </FormLayout.Row>
          </FormLayout.SubSection>
        </FormLayout.Section>
        <FormLayout.Actions>
          <button type="button">Annuler</button>
          <button type="button">Envoyer</button>
        </FormLayout.Actions>
      </FormLayout>
    </div>
  )
}

const DemoInformationBox = () => (
  <div>
    <h4>Information sur champs</h4>
    <p>
      Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor
      sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet
      Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet
    </p>
  </div>
)

const DesignedFormLayout = (args: FormLayoutProps) => (
  <div style={{ width: 850 }}>
    <FormLayout {...args}>
      <FormLayout.Section
        description="Lorem ipsum dolor sit amet"
        title="Lorem ipsum dolor sit amet"
      >
        <FormLayout.Row sideComponent={<DemoInformationBox />}>
          <TextInput label="Nom" name="lastname" />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput label="Tel" name="Tel" />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput label="Mail" name="mail" />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput label="Jambon" name="ham" />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section
        description="Lorem ipsum dolor sit amet"
        title="Lorem ipsum dolor sit amet"
      >
        <FormLayout.Row sideComponent={null}>
          <TextInput label="Prénom" name="firstname" />
        </FormLayout.Row>
        <FormLayout.SubSection title="Sub section title">
          <FormLayout.Row inline sideComponent={<DemoInformationBox />}>
            <>
              <TextInput label="Prénom" name="firstname" />
              <TextInput label="Nom" name="lastname" />
            </>
          </FormLayout.Row>
        </FormLayout.SubSection>
      </FormLayout.Section>
      <FormLayout.Actions>
        <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
        <Button>Envoyer</Button>
      </FormLayout.Actions>
    </FormLayout>
  </div>
)

export const Default: StoryObj<typeof FormLayout> = {
  render: () => <DefaultFormLayout>test</DefaultFormLayout>,
}

export const Designed = {
  render: () => <DesignedFormLayout fullWidthActions>test</DesignedFormLayout>,
}

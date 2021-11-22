import React from 'react'

import FormLayout from './FormLayout'

export default {
  title: 'components/FormLayout',
  component: FormLayout,
}

const Template = () => (
  <div style={{ width: 780 }}>
    <FormLayout>
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

export const Default = Template.bind({})

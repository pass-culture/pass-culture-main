import { Formik } from 'formik'
import React from 'react'

import { Button, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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

const DemoInformationBox = () => (
  <div>
    <h4>Information sur champs</h4>
    <p>
      Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor
      sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet{' '}
    </p>
  </div>
)

const TemplateDesigned = () => (
  <div style={{ width: 850 }}>
    <Formik initialValues={{}} onSubmit={() => alert('Form submit !')}>
      <FormLayout>
        <FormLayout.Section
          description="Lorem ipsum dolor sit amet"
          title="Lorem ipsum dolor sit amet"
        >
          <FormLayout.RowWithInfo>
            <TextInput label="Nom" name="lastname" />
            <DemoInformationBox />
          </FormLayout.RowWithInfo>
        </FormLayout.Section>
        <FormLayout.Section
          description="Lorem ipsum dolor sit amet"
          title="Lorem ipsum dolor sit amet"
        >
          <FormLayout.RowWithInfo>
            <TextInput label="Prénom" name="firstname" />
            <DemoInformationBox />
          </FormLayout.RowWithInfo>
          <FormLayout.SubSection title="Sub section title">
            <FormLayout.RowWithInfo inline>
              <>
                <TextInput label="Prénom" name="firstname" />
                <TextInput label="Nom" name="lastname" />
              </>
              <DemoInformationBox />
            </FormLayout.RowWithInfo>
          </FormLayout.SubSection>
        </FormLayout.Section>
        <FormLayout.Actions>
          <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          <Button>Envoyer</Button>
        </FormLayout.Actions>
      </FormLayout>
    </Formik>
  </div>
)

export const Designed = TemplateDesigned.bind({})

const TemplateWithInfo = () => (
  <div style={{ width: 780 }}>
    <FormLayout>
      <FormLayout.Section
        description="Lorem ipsum dolor sit amet"
        title="Lorem ipsum dolor sit amet"
      >
        <FormLayout.RowWithInfo>
          <label>
            Hello
            <input type="text" />
          </label>
          <div>Information box</div>
        </FormLayout.RowWithInfo>
      </FormLayout.Section>
      <FormLayout.Section
        description="Lorem ipsum dolor sit amet"
        title="Lorem ipsum dolor sit amet"
      >
        <FormLayout.RowWithInfo>
          <label>
            Hello
            <input type="text" />
          </label>
          <div>Information box</div>
        </FormLayout.RowWithInfo>
        <FormLayout.SubSection title="Sub section title">
          <FormLayout.RowWithInfo inline>
            <>
              <label>
                Hello
                <input type="text" />
              </label>
              <label>
                Hello
                <input type="text" />
              </label>
            </>
            <div>Information box</div>
          </FormLayout.RowWithInfo>
        </FormLayout.SubSection>
      </FormLayout.Section>
      <FormLayout.Actions>
        <button type="button">Annuler</button>
        <button type="button">Envoyer</button>
      </FormLayout.Actions>
    </FormLayout>
  </div>
)

export const WithInfo = TemplateWithInfo.bind({})

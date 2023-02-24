import React from 'react'

import FormLayout from 'components/FormLayout'
import { RadioButton } from 'ui-kit'

export const RecurrenceForm = () => {
  return (
    <form>
      <FormLayout.Section title="Ajouter une récurrence">
        <fieldset>
          <legend>Cet évènement aura lieu</legend>
        </fieldset>
      </FormLayout.Section>
    </form>
  )
}

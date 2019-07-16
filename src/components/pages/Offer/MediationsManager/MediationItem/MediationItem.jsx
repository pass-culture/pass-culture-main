import { Field, Form } from 'pass-culture-shared'
import React from 'react'

const MediationItem = ({ mediation }) => {
  const { id, isActive, thumbUrl } = mediation || {}
  return (
    <Form
      Tag="li"
      action={`/mediations/${id}`}
      handleSuccessNotification={null}
      isAutoSubmit
      name={`mediation-${id}`}
      patch={mediation}
    >
      <img
        alt={`accroche-${id}`}
        disabled={!isActive}
        src={thumbUrl}
      />
      <br />
      <br />
      <div className="columns is-centered">
        <Field
          name="isActive"
          type="checkbox"
        />
      </div>
    </Form>
  )
}

export default MediationItem

import {Field, Form} from 'pass-culture-shared'
import React from 'react'
import PropTypes from "prop-types"

const MediationItem = ({ mediation }) => {
  const { id, isActive, thumbUrl } = mediation || {}
  return (
    <Form
      action={`/mediations/${id}`}
      handleSuccessNotification={null}
      isAutoSubmit
      name={`mediation-${id}`}
      patch={mediation}
      Tag="li"
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

MediationItem.defaultProps = {
  mediation: { thumbUrl: '' }
}

MediationItem.propTypes = {
  mediation: PropTypes.shape(
    {
     id: PropTypes.string.isRequired,
     isActive: PropTypes.bool.isRequired,
     thumbUrl: PropTypes.string
    }
  ),
}

export default MediationItem

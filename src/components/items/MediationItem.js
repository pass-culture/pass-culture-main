import { Field, Form } from 'pass-culture-shared'
import React, { Component } from 'react'

import { THUMBS_URL } from '../../utils/config'

class MediationItem extends Component {
  render() {
    const { mediation } = this.props
    const { id } = mediation || {}
    return (
      <Form
        action={`/mediations/${id}`}
        isAutoSubmit
        name={`mediation-${id}`}
        patch={mediation}
        Tag="li">
        <img alt={`accroche-${id}`} src={`${THUMBS_URL}/mediations/${id}`} />
        <Field name="isActive" type="checkbox" />
      </Form>
    )
  }
}

export default MediationItem

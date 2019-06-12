import React, { PureComponent } from 'react'
import {Field, Form} from "pass-culture-shared";

export class SelectDigitalOffer extends PureComponent {
  constructor() {
    super()
    this.state = {isDigital: false}
    this.handleIsDigitalChecked = this.handleIsDigitalChecked.bind(this)
  }

  handleIsDigitalChecked = event => {
    //const isChecked = document.getElementById("isDigital").checked
    const { checked } = this.checked
    console.log(checked)
    this.setState({isDigital: event.target.checked })
  }

  render() {
    return (
      <Form
        action="/bookings"
        name="digitalOffer"
        Tag={null}>
        <h2>
          {'ou :'}
        </h2>
        <div className="field-group">
          <Field
            id="isDigital"
            type="checkbox"
            label="Cocher cette case pour voir les offres numériques"
            checked={this.state.isDigital}
            onChange={this.handleIsDigitalChecked}
          />
        </div>
      </Form>

    )
  }
}

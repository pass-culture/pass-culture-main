/**
 * This addon adds support for form field (PcFormField).
 *
 * Form fields can be used to group multiple fields into one.
 *
 */
class PcFormField extends PcAddOn {

  initialize = () => {
    document.querySelectorAll(".pc-form-field-empty-container").forEach(($emptyFormField) => {
      $emptyFormField.querySelectorAll(".value-element-form").forEach(($valueElementForm) => {
        $valueElementForm.removeAttribute("name")
        $valueElementForm.removeAttribute("id")
      })
    });
  }

}

/**
 * Configure TomSelect on a `<select multiple />`.
 *
 * In the front-end business, we note two types of tom select instances:
 * 1. select multiple field.
 * 2. select multiple field with xhr autocomplete.
 *
 * @example
 * // select multiple field
 * <select multiple class="pc-select-multiple-field">
 *   <option value="1">item #1</option>
 *   <option value="2">item #2</option>
 * </select>
 *
 * @example
 * // select multiple field with xhr autocomplete.
 * // In this example, our backend automatically sets data attributes, this allows the initial render to have the initialValues
 * <select
 *   multiple
 *   class="pc-select-multiple-field pc-select-multiple-autocomplete-field"
 *   data-tomselect-autocomplete-url="/backofficev3/autocomplete/offerers"
 *   data-tomselect-options="[{\"id\": \"84\", \"text\": \"Cin\u00e9ma - CGR (00000003800058)\"}]"
 *   data-tomselect-items="[\"84\"]"
 * ></select>
 */
class PcSelectMultipleField extends PcAddOn {
  static SELECT_MULTIPLE_SELECTOR = 'select.pc-select-multiple-field[multiple]'
  static SELECT_MULTIPLE_AUTOCOMPLETE_CLASS = 'pc-select-multiple-autocomplete-field'
  static SELECT_MULTIPLE_SETTINGS = {
    plugins: ['dropdown_input', 'clear_button', 'checkbox_options'],
    persist: false,
    create: false,
  }

  state = {
    selects: []
  }

  get $selects() {
    return document.querySelectorAll(PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR)
  }

  bindEvents = () => {
    this.$selects.forEach(($select) => {
      const settingsXhrAutocomplete = $select.classList.contains(PcSelectMultipleField.SELECT_MULTIPLE_AUTOCOMPLETE_CLASS) ?
        this.#getSettingsXhrAutocomplete($select) :
        {}
      if (!$select.tomselect) {
        this.state.selects.push(new TomSelect($select, {
          ...PcSelectMultipleField.SELECT_MULTIPLE_SETTINGS,
          ...settingsXhrAutocomplete,
        }))
      }
    })
    EventHandler.on(document.body, 'mousemove', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this._preventDefault)
    EventHandler.on(document.body, 'mousedown', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onMouseDown)
    EventHandler.on(document.body, 'change', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onScrollOrChange)
    EventHandler.on(document.body, 'scroll', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onScrollOrChange)
  }

  unbindEvents = () => {
    // NOTE: destroy method unbind event but also destroy the HTML initialized by TomSelect which cause a UX glitch.
    // Since we do not have control nor want to maintain tom select lib, until a better method exist to unbind/rebind
    // We tolerate it's deactivation
    // See https://github.com/orchidjs/tom-select/discussions/569 for resolution
    // this.state.selects.forEach((select) => select.destroy())

    EventHandler.off(document.body, 'mousemove', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this._preventDefault)
    EventHandler.off(document.body, 'mousedown', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onMouseDown)
    EventHandler.off(document.body, 'change', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onScrollOrChange)
    EventHandler.off(document.body, 'scroll', PcSelectMultipleField.SELECT_MULTIPLE_SELECTOR, this.#onScrollOrChange)
  }

  #onMouseDown(event) {
    event.preventDefault()
    const scrollTop = event.target.scrollTop
    event.target.selected = !event.target.selected
    setTimeout(() => {
      event.target.scrollTop = scrollTop
    })
    event.target.focus()
  }

  #onScrollOrChange(event) {
    var selected = [...event.target.options].filter((option) => option.selected)

    if (selected.length > 0) {
      event.target.parentElement.querySelector('label').classList.add('d-none')
      return
    }
    event.target.parentElement.querySelector('label').classList.remove('d-none')
  }

  #getSettingsXhrAutocomplete($select) {
    const {
      tomselectAutocompleteUrl,
      tomselectOptions,
      tomselectItems,
    } = $select.dataset
    return {
      valueField: 'id',
      labelField: 'text',
      load: (query, callback) => {
        const url = `${tomselectAutocompleteUrl}?q=${encodeURIComponent(query)}`;
        fetch(url)
          .then((response) => response.json())
          .then((json) => callback(json.items))
          .catch((error) => callback(undefined, error))
      },
      render: {
        no_results: (data, escape) => {
          return '<div class="no-results">Aucun résultat pour "' + escape(data.input) + '"</div>'
        },
      },
      ...(tomselectOptions ? { options: JSON.parse(tomselectOptions) } : {}),
      ...(tomselectItems ? { items: JSON.parse(tomselectItems) } : {}),
    }
  }
}

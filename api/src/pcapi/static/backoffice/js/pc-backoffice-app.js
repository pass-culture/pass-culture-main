class PcBackofficeApp {
  constructor() {
    this.bindEvents()
    this.initializePcSelects()
  }

  get $pcSelects() {
    return document.querySelectorAll('.pc-select')
  }

  get $forms() {
    return document.forms
  }

  bindEvents = () => {
    this.$forms.forEach(($form) => {
      $form.addEventListener("submit", (event) => {
        event.preventDefault();
        const form = event.target;
        if (form.checkValidity()) {
          form.submit();
        }
      }, false);
    })
  }

  initializePcSelects = () => {
    this.$pcSelects.forEach(($pcSelect) => {
      const settings = {
        plugins: ['dropdown_input', 'clear_button', 'checkbox_options'],
        persist: false,
        create: false,

      };
      new TomSelect($pcSelect, settings);
    })
  }
}

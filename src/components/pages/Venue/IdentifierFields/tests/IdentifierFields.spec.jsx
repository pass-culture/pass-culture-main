/*
it('should display a hidden Field component', () => {
 // when
 const wrapper = shallow(<Venue {...props} />)

  // then
 const field = wrapper
   .find(Form)
   .find(Field)
   .first()
 expect(field).toBeDefined()
 expect(field.prop('type')).toBe('hidden')
 expect(field.prop('name')).toBe('managingOffererId')
})

it('should display a comment Field component', () => {
 // when
 const wrapper = shallow(<Venue {...props} />)

  // then
 const firstFieldGroup = wrapper.find('.field-group').first()
 const lastField = firstFieldGroup.find(Field).last()
 expect(lastField).toBeDefined()
 expect(lastField.prop('label')).toBe('Commentaire (si pas de SIRET)')
 expect(lastField.prop('name')).toBe('comment')
 expect(lastField.prop('type')).toBe('textarea')
 expect(lastField.prop('required')).toBe(false)
})

*/

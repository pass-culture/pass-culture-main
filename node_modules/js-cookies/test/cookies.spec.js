import cookies from '../src/cookies';
import shold from 'should';

describe('Cookies', function () {
  it('#setItem() should set a value', function () {
    cookies.setItem('name', '==xx');
    document.cookie.indexOf('%3D%3Dxx').should.not.be.equal(-1);
  });

  it('#getItem() should return true', function () {
    cookies.setItem('age', '=x');
    const age = cookies.getItem('age');
    age.should.be.equal('=x');

  });

  it('#hasItem() should return a boolean', function () {
    cookies.setItem('age', 24);
    cookies.hasItem('age').should.be.equal(true);
    cookies.removeItem('age')
    cookies.hasItem('age').should.be.equal(false);
  })

  it('#keys() should return a array', function () {
    cookies.setItem('name', 'duian');
    cookies.setItem('age', 24);
    cookies.keys().length.should.be.equal(2);
  });

  it('#removeItem() should remove item', function () {
    cookies.setItem('age', 24);
    cookies.removeItem('age')
    cookies.hasItem('age').should.not.be.equal(true);
  });

})

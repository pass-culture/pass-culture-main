import{r as s}from"./index-76fb7be0.js";var T={exports:{}},_={};/**
 * @license React
 * use-sync-external-store-shim.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var f=s;function w(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var $=typeof Object.is=="function"?Object.is:w,R=f.useState,g=f.useEffect,V=f.useLayoutEffect,k=f.useDebugValue;function A(t,e){var n=e(),o=R({inst:{value:n,getSnapshot:e}}),r=o[0].inst,u=o[1];return V(function(){r.value=n,r.getSnapshot=e,p(r)&&u({inst:r})},[t,n,e]),g(function(){return p(r)&&u({inst:r}),t(function(){p(r)&&u({inst:r})})},[t]),k(n),n}function p(t){var e=t.getSnapshot;t=t.value;try{var n=e();return!$(t,n)}catch{return!0}}function D(t,e){return e()}var H=typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"?D:A;_.useSyncExternalStore=f.useSyncExternalStore!==void 0?f.useSyncExternalStore:H;T.exports=_;var j=T.exports,F={};/**
 * @license React
 * use-sync-external-store-shim/with-selector.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var v=s,K=j;function B(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var L=typeof Object.is=="function"?Object.is:B,M=K.useSyncExternalStore,W=v.useRef,q=v.useEffect,P=v.useMemo,Y=v.useDebugValue;F.useSyncExternalStoreWithSelector=function(t,e,n,o,r){var u=W(null);if(u.current===null){var i={hasValue:!1,value:null};u.current=i}else i=u.current;u=P(function(){function C(c){if(!h){if(h=!0,d=c,c=o(c),r!==void 0&&i.hasValue){var a=i.value;if(r(a,c))return x=a}return x=c}if(a=x,L(d,c))return a;var O=o(c);return r!==void 0&&r(a,O)?a:(d=c,x=O)}var h=!1,d,x,y=n===void 0?null:n;return[function(){return C(e())},y===null?void 0:function(){return C(y())}]},[e,n,o,r]);var S=M(t,u[0],u[1]);return q(function(){i.hasValue=!0,i.value=S},[S]),Y(S),S};const E=Symbol.for("react-redux-context"),I=typeof globalThis<"u"?globalThis:{};function z(){var t;if(!s.createContext)return{};const e=(t=I[E])!=null?t:I[E]=new Map;let n=e.get(s.createContext);return n||(n=s.createContext(null),e.set(s.createContext,n)),n}const l=z();function m(t=l){return function(){return s.useContext(t)}}const G=m();function N(t=l){const e=t===l?G:m(t);return function(){const{store:o}=e();return o}}const J=N();function Q(t=l){const e=t===l?J:N(t);return function(){return e().dispatch}}const tt=Q(),U="SET_IS_STICKYBAR_OPEN",X="CLOSE_NOTIFICATION",Z="SHOW_NOTIFICATION",et=t=>({payload:t,type:Z}),nt=()=>({type:X}),rt=t=>({payload:t,type:U});export{et as a,nt as c,rt as s,tt as u};

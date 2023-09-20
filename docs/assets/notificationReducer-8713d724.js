import{r as s}from"./index-76fb7be0.js";import{r as k}from"./index-b0fbc9cc.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./react-is.production.min-a192e302.js";var I={exports:{}},T={};/**
 * @license React
 * use-sync-external-store-shim.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var f=s;function B(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var V=typeof Object.is=="function"?Object.is:B,A=f.useState,D=f.useEffect,H=f.useLayoutEffect,j=f.useDebugValue;function F(t,e){var n=e(),r=A({inst:{value:n,getSnapshot:e}}),o=r[0].inst,u=r[1];return H(function(){o.value=n,o.getSnapshot=e,v(o)&&u({inst:o})},[t,n,e]),D(function(){return v(o)&&u({inst:o}),t(function(){v(o)&&u({inst:o})})},[t]),j(n),n}function v(t){var e=t.getSnapshot;t=t.value;try{var n=e();return!V(t,n)}catch{return!0}}function K(t,e){return e()}var L=typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"?K:F;T.useSyncExternalStore=f.useSyncExternalStore!==void 0?f.useSyncExternalStore:L;I.exports=T;var M=I.exports,W={};/**
 * @license React
 * use-sync-external-store-shim/with-selector.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var d=s,q=M;function P(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var Y=typeof Object.is=="function"?Object.is:P,U=q.useSyncExternalStore,z=d.useRef,G=d.useEffect,J=d.useMemo,Q=d.useDebugValue;W.useSyncExternalStoreWithSelector=function(t,e,n,r,o){var u=z(null);if(u.current===null){var i={hasValue:!1,value:null};u.current=i}else i=u.current;u=J(function(){function h(c){if(!y){if(y=!0,x=c,c=r(c),o!==void 0&&i.hasValue){var a=i.value;if(o(a,c))return S=a}return S=c}if(a=S,Y(x,c))return a;var O=r(c);return o!==void 0&&o(a,O)?a:(x=c,S=O)}var y=!1,x,S,C=n===void 0?null:n;return[function(){return h(e())},C===null?void 0:function(){return h(C())}]},[e,n,r,o]);var p=U(t,u[0],u[1]);return G(function(){i.hasValue=!0,i.value=p},[p]),Q(p),p};function X(t){t()}let _=X;const Z=t=>_=t,it=()=>_,m=Symbol.for("react-redux-context"),E=typeof globalThis<"u"?globalThis:{};function b(){var t;if(!s.createContext)return{};const e=(t=E[m])!=null?t:E[m]=new Map;let n=e.get(s.createContext);return n||(n=s.createContext(null),e.set(s.createContext,n)),n}const l=b();function N(t=l){return function(){return s.useContext(t)}}const tt=N();function w(t=l){const e=t===l?tt:N(t);return function(){const{store:r}=e();return r}}const et=w();function nt(t=l){const e=t===l?et:w(t);return function(){return e().dispatch}}const at=nt();Z(k.unstable_batchedUpdates);const R="SET_IS_STICKYBAR_OPEN",g="CLOSE_NOTIFICATION",$="SHOW_NOTIFICATION",ft=t=>({payload:t,type:$}),lt=()=>({type:g}),pt=t=>({payload:t,type:R}),ot={isStickyBarOpen:!1,notification:null},St=(t=ot,e)=>{switch(e.type){case g:return{...t,notification:null};case $:return{...t,notification:e.payload};case R:return{...t,isStickyBarOpen:e.payload};default:return t}};export{l as R,pt as a,lt as c,it as g,St as n,ft as s,at as u};
//# sourceMappingURL=notificationReducer-8713d724.js.map

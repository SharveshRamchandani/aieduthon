import React from 'react';
import styled from 'styled-components';

const Animation1 = () => {
  return (
    <StyledWrapper>
      <div className="container">
         <div className="laptop-wrapper">
        <div className="macbook">
          <div className="macbook__topBord">
            <div className="macbook__display">
              <div className="macbook__load" />
            </div>
          </div>
          <div className="macbook__underBord">
            <div className="macbook__keybord">
              <div className="keybord">
                <div className="keybord__touchbar" />
                <ul className="keybord__keyBox">
                  <li className="keybord__key key--01" />
                  <li className="keybord__key key--02" />
                  <li className="keybord__key key--03" />
                  <li className="keybord__key key--04" />
                  <li className="keybord__key key--05" />
                  <li className="keybord__key key--06" />
                  <li className="keybord__key key--07" />
                  <li className="keybord__key key--08" />
                  <li className="keybord__key key--09" />
                  <li className="keybord__key key--10" />
                  <li className="keybord__key key--11" />
                  <li className="keybord__key key--12" />
                  <li className="keybord__key key--13" />
                </ul>
                <ul className="keybord__keyBox--under">
                  <li className="keybord__key key--14" />
                  <li className="keybord__key key--15" />
                  <li className="keybord__key key--16" />
                  <li className="keybord__key key--17" />
                  <li className="keybord__key key--18" />
                  <li className="keybord__key key--19" />
                  <li className="keybord__key key--20" />
                  <li className="keybord__key key--21" />
                  <li className="keybord__key key--22" />
                  <li className="keybord__key key--23" />
                  <li className="keybord__key key--24" />
                </ul>
              </div>
            </div>
          </div>
        </div>
        </div>
     
       <div className="dog-wrapper">
        <div className="dog">
          <div className="dog__paws">
            <div className="dog__bl-leg leg">
              <div className="dog__bl-paw paw" />
              <div className="dog__bl-top top" />
            </div>
            <div className="dog__fl-leg leg">
              <div className="dog__fl-paw paw" />
              <div className="dog__fl-top top" />
            </div>
            <div className="dog__fr-leg leg">
              <div className="dog__fr-paw paw" />
              <div className="dog__fr-top top" />
            </div>
          </div>
          <div className="dog__body">
            <div className="dog__tail" />
          </div>
          <div className="dog__head">
            <div className="dog__snout">
              <div className="dog__nose" />
              <div className="dog__eyes">
                <div className="dog__eye-l" />
                <div className="dog__eye-r" />
              </div>
            </div>
          </div>
          <div className="dog__head-c">
            <div className="dog__ear-l" />
            <div className="dog__ear-r" />
          </div>
        </div>
       </div>
       </div>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
 .container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 80px;               
  width: 60vh;
  height: 60vh ;
}

  .macbook {
    position: relative;
    width: 228px;
    height: 260px;
  }
  .macbook__topBord {
    position: absolute;
    z-index: 0;
    top: 34px;
    left: 0;
    width: 128px;
    height: 116px;
    border-radius: 6px;
    transform-origin: center;
    background: linear-gradient(-135deg, #c8c9c9 52%, #8c8c8c 56%);
    transform: scale(0) skewY(-30deg);
    animation: topbord 0.4s 1.7s ease-out;
    animation-fill-mode: forwards;
  }
  .macbook__topBord::before {
    content: "";
    position: absolute;
    z-index: 2;
    top: 8px;
    left: 6px;
    width: 100%;
    height: 100%;
    border-radius: 6px;
    background: #000;
  }
  .macbook__topBord::after {
    content: "";
    position: absolute;
    z-index: 1;
    bottom: -7px;
    left: 8px;
    width: 168px;
    height: 12px;
    transform-origin: left bottom;
    transform: rotate(-42deg) skew(-4deg);
    background: linear-gradient(-135deg, #c8c9c9 52%, #8c8c8c 56%);
  }
  .macbook__display {
    position: absolute;
    z-index: 10;
    top: 17px;
    left: 12px;
    z-index: 2;
    width: calc(100% - 12px);
    height: calc(100% - 18px);
    background: linear-gradient(45deg, #3ba9ff, #c82aff);
  }
  .macbook__display::before {
    content: "";
    position: absolute;
    z-index: 5;
    top: -9px;
    left: -6px;
    width: calc(100% + 12px);
    height: calc(100% + 18px);
    border-radius: 6px;
    background: linear-gradient(
      60deg,
      rgba(255, 255, 255, 0) 60%,
      rgba(255, 255, 255, 0.3) 60%
    );
  }
  .macbook__load {
    position: relative;
    width: 100%;
    height: 100%;
    background: #222;
    animation: display 0.4s 4.3s ease;
    opacity: 1;
    animation-fill-mode: forwards;
  }
  .macbook__load:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    margin: auto;
    width: 80px;
    height: 6px;
    border-radius: 3px;
    box-sizing: border-box;
    border: solid 1px #fff;
  }
  .macbook__load:after {
    content: "";
    position: absolute;
    top: 0;
    left: 18px;
    bottom: 0;
    margin: auto;
    width: 0;
    height: 6px;
    border-radius: 3px;
    background: #fff;
    animation: load 2s 2s ease-out;
    animation-fill-mode: forwards;
  }
  .macbook__underBord {
    position: relative;
    left: 42px;
    bottom: -145px;
    width: 150px;
    height: 90px;
    border-radius: 6px;
    transform-origin: center;
    transform: rotate(-30deg) skew(30deg);
    background: linear-gradient(-45deg, #c8c9c9 61%, #8c8c8c 66%);
    animation: modal 0.5s 1s ease-out;
    opacity: 0;
    animation-fill-mode: forwards;
  }
  .macbook__underBord::before {
    content: "";
    position: absolute;
    z-index: 3;
    top: -8px;
    left: 8px;
    width: 100%;
    height: 100%;
    border-radius: 6px;
    background: #dcdede;
  }
  .macbook__underBord::after {
    content: "";
    position: absolute;
    z-index: 2;
    top: -8px;
    left: 12px;
    width: 170px;
    height: 15px;
    transform-origin: top left;
    background: linear-gradient(-45deg, #c8c9c9 61%, #8c8c8c 66%);
    transform: rotate(31deg) skew(-16deg);
  }
  .macbook__keybord {
    position: relative;
    top: 0;
    left: 16px;
    z-index: 3;
    border-radius: 3px;
    width: calc(100% - 16px);
    height: 45px;
    background: #c8c9c9;
  }
  .macbook__keybord::before {
    content: "";
    position: absolute;
    bottom: -30px;
    left: 0;
    right: 0;
    margin: 0 auto;
    width: 40px;
    height: 25px;
    border-radius: 3px;
    background: #c8c9c9;
  }
  .keybord {
    position: relative;
    top: 2px;
    left: 2px;
    display: flex;
    flex-direction: column;
    width: calc(100% - 3px);
    height: calc(100% - 4px);
  }
  .keybord__touchbar {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: #000;
  }
  .keybord__keyBox {
    display: grid;
    grid-template-rows: 3fr 1fr;
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
    width: 100%;
    height: 24px;
    margin: 1px 0 0 0;
    padding: 0 0 0 1px;
    box-sizing: border-box;
    list-style: none;
  }
  .keybord__key {
    position: relative;
    width: 8px;
    height: 7px;
    margin: 1px;
    background: #000;
  }
  .keybord__keyBox .keybord__key {
    transform: translate(60px, -60px);
    animation: key 0.2s 1.4s ease-out;
    animation-fill-mode: forwards;
    opacity: 0;
  }
  .keybord__keyBox .keybord__key::before,
  .keybord__keyBox .keybord__key::after {
    content: "";
    position: absolute;
    left: 0;
    width: 100%;
    height: 100%;
    background: #000;
  }
  .keybord__key::before {
    top: 8px;
    transform: translate(20px, -20px);
    animation: key1 0.2s 1.5s ease-out;
    animation-fill-mode: forwards;
  }
  .keybord__key::after {
    top: 16px;
    transform: translate(40px, -40px);
    animation: key2 0.2s 1.6s ease-out;
    animation-fill-mode: forwards;
  }
  .keybord__keyBox .key--12::before {
    width: 10px;
  }
  .keybord__keyBox .key--13::before {
    height: 10px;
  }
  .key--01 {
    grid-row: 1 / 2;
    grid-column: 1 / 2;
  }
  .key--02 {
    grid-row: 1 / 2;
    grid-column: 2 / 3;
  }
  .key--03 {
    grid-row: 1 / 2;
    grid-column: 3 / 4;
  }
  .key--04 {
    grid-row: 1 / 2;
    grid-column: 4 / 5;
  }
  .key--05 {
    grid-row: 1 / 2;
    grid-column: 5 / 6;
  }
  .key--06 {
    grid-row: 1 / 2;
    grid-column: 6 / 7;
  }
  .key--07 {
    grid-row: 1 / 2;
    grid-column: 7 / 8;
  }
  .key--08 {
    grid-row: 1 / 2;
    grid-column: 8 / 9;
  }
  .key--09 {
    grid-row: 1 / 2;
    grid-column: 9 / 10;
  }
  .key--10 {
    grid-row: 1 / 2;
    grid-column: 10 / 11;
  }
  .key--11 {
    grid-row: 1 / 2;
    grid-column: 11 / 12;
  }
  .key--12 {
    grid-row: 1 / 2;
    grid-column: 12 / 13;
  }
  .key--13 {
    grid-row: 1 / 2;
    grid-column: 13 / 14;
  }
  .keybord__keyBox--under {
    margin: 0;
    padding: 0 0 0 1px;
    box-sizing: border-box;
    list-style: none;
    display: flex;
  }
  .keybord__keyBox--under .keybord__key {
    transform: translate(80px, -80px);
    animation: key3 0.3s 1.6s linear;
    animation-fill-mode: forwards;
    opacity: 0;
  }
  .key--19 {
    width: 28px;
  }
  @keyframes topbord {
    0% {
      transform: scale(0) skewY(-30deg);
    }
    30% {
      transform: scale(1.1) skewY(-30deg);
    }
    45% {
      transform: scale(0.9) skewY(-30deg);
    }
    60% {
      transform: scale(1.05) skewY(-30deg);
    }
    75% {
      transform: scale(0.95) skewY(-30deg);
    }
    90% {
      transform: scale(1.02) skewY(-30deg);
    }
    100% {
      transform: scale(1) skewY(-30deg);
    }
  }
  @keyframes display {
    0% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }

  @keyframes load {
    0% {
      width: 0;
    }
    20% {
      width: 40px;
    }
    30% {
      width: 40px;
    }
    60% {
      width: 60px;
    }
    90% {
      width: 60px;
    }
    100% {
      width: 80px;
    }
  }

  @keyframes modal {
    0% {
      transform: scale(0) rotate(-60deg) skew(30deg);
      opacity: 0;
    }
    30% {
      transform: scale(1.1) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
    45% {
      transform: scale(0.9) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
    60% {
      transform: scale(1.05) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
    75% {
      transform: scale(0.95) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
    90% {
      transform: scale(1.02) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
    100% {
      transform: scale(1) rotate(-30deg) skew(30deg);
      opacity: 1;
    }
  }

  @keyframes key {
    0% {
      transform: translate(60px, -60px);
      opacity: 0;
    }
    100% {
      transform: translate(0px, 0px);
      opacity: 1;
    }
  }
  @keyframes key1 {
    0% {
      transform: translate(20px, -10px);
      opacity: 0;
    }
    100% {
      transform: translate(0px, 0px);
      opacity: 1;
    }
  }
  @keyframes key2 {
    0% {
      transform: translate(40px, -40px);
      opacity: 0;
    }
    100% {
      transform: translate(0px, 0px);
      opacity: 1;
    }
  }
  @keyframes key3 {
    0% {
      transform: translate(80px, -80px);
      opacity: 0;
    }
    100% {
      transform: translate(0px, 0px);
      opacity: 1;
    }
}
    .leg {
    position: absolute;
    bottom: 0;
    width: 2vmax;
    height: 2.125vmax;
  }

  .paw {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 1.95vmax;
    height: 1.875vmax;
    overflow: hidden;
  }

  .paw::before {
    content: "";
    position: absolute;
    width: 3.75vmax;
    height: 3.75vmax;
    border-radius: 50%;
  }

  .top {
    position: absolute;
    bottom: 0;
    left: 0.75vmax;
    height: 2.5vmax;
    width: 2.625vmax;
    border-top-left-radius: 1.425vmax;
    border-top-right-radius: 1.425vmax;
    transform-origin: bottom right;
    transform: rotateZ(90deg) translateX(-0.1vmax) translateY(1.5vmax);
    z-index: -1;
    background-image: linear-gradient(70deg, transparent 20%, #ff8b56 20%);
  }

  .dog {
    position: relative;
    width: 20vmax;
    height: 8vmax;
  }

  .dog::before {
    content: "";
    position: absolute;
    bottom: -0.75vmax;
    right: -0.15vmax;
    width: 100%;
    height: 1.5vmax;
    background-color: rgba(28, 49, 48, 0.1);
    border-radius: 50%;
    z-index: -1000;
    animation: shadow 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__head {
    position: absolute;
    left: 2vmax;
    bottom: 0;
    width: 9.75vmax;
    height: 8.25vmax;
    border-top-left-radius: 4.05vmax;
    border-top-right-radius: 4.05vmax;
    border-bottom-right-radius: 3.3vmax;
    border-bottom-left-radius: 3.3vmax;
    background-color: #ff8147;
    animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__head-c {
    position: absolute;
    left: 1.5vmax;
    bottom: 0;
    width: 9.75vmax;
    height: 8.25vmax;
    animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
    z-index: -1;
  }

  .dog__snout {
    position: absolute;
    left: -1.5vmax;
    bottom: 0;
    width: 7.5vmax;
    height: 3.75vmax;
    border-top-right-radius: 3vmax;
    border-bottom-right-radius: 3vmax;
    border-bottom-left-radius: 4.5vmax;
    background-color: #d7dbd2;
    animation: snout 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__snout::before {
    content: "";
    position: absolute;
    left: -0.1125vmax;
    top: -0.15vmax;
    width: 1.875vmax;
    height: 1.125vmax;
    border-top-right-radius: 3vmax;
    border-bottom-right-radius: 3vmax;
    border-bottom-left-radius: 4.5vmax;
    background-color: #1c3130;
    animation: snout-b 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__nose {
    position: absolute;
    top: -1.95vmax;
    left: 40%;
    width: 0.75vmax;
    height: 2.4vmax;
    border-radius: 0.525vmax;
    transform-origin: bottom;
    transform: rotateZ(10deg);
    background-color: #d7dbd2;
  }

  .dog__eye-l,
  .dog__eye-r {
    position: absolute;
    top: -0.9vmax;
    width: 0.675vmax;
    height: 0.375vmax;
    border-radius: 50%;
    background-color: #1c3130;
    animation: eye 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__eye-l {
    left: 27%;
  }

  .dog__eye-r {
    left: 65%;
  }

  

  .dog__ear-l {
    top: 1.5vmax;
    left: 6vmax;
    transform-origin: bottom left;
    transform: rotateZ(-50deg);
    z-index: -1;
    animation: ear-l 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__ear-r {
    top: 1.5vmax;
    right: 3vmax;
    transform-origin: bottom right;
    transform: rotateZ(20deg);
    z-index: -2;
    animation: ear-r 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__body {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    position: absolute;
    bottom: 0.3vmax;
    left: 3.75vmax;
    width: 18.75vmax;
    height: 7.2vmax;
    border-top-left-radius: 3vmax;
    border-top-right-radius: 6vmax;
    border-bottom-right-radius: 1.5vmax;
    border-bottom-left-radius: 6vmax;
    background-color: #ff702e;
    z-index: -2;
    animation: body 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  }

  .dog__tail {
    position: absolute;
    right: -3vmax;
    height: 1.5vmax;
    width: 4.5vmax;
    background-color: #e96839;
    border-radius: 1.5vmax;
  }

  .dog__paws {
    position: absolute;
    bottom: 0;
    left: 7.5vmax;
    width: 12vmax;
    height: 3vmax;
  }

  .dog__bl-leg {
    left: -3vmax;
    z-index: -10;
  }

  .dog__bl-paw::before {
    background-color: #bec4b6;
  }

  .dog__bl-top {
    background-image: linear-gradient(80deg, transparent 20%, #e96839 20%);
  }

  .dog__fl-leg {
    z-index: 10;
    left: 0;
  }

  .dog__fl-paw::before {
    background-color: #d7dbd2;
  }

  .dog__fr-leg {
    right: 0;
  }

  .dog__fr-paw::before {
    background-color: #d7dbd2;
  }

  /*==============================*/

  @keyframes head {
    0%,
    10%,
    20%,
    26%,
    28%,
    90%,
    100% {
      height: 8.25vmax;
      bottom: 0;
      transform-origin: bottom right;
      transform: rotateZ(0);
    }
    5%,
    15%,
    22%,
    24%,
    30% {
      height: 8.1vmax;
    }
    32%,
    50% {
      height: 8.25vmax;
    }
    55%,
    60% {
      bottom: 0.75vmax;
      transform-origin: bottom right;
      transform: rotateZ(0);
    }
    70%,
    80% {
      bottom: 0.75vmax;
      transform-origin: bottom right;
      transform: rotateZ(10deg);
    }
  }

  @keyframes body {
    0%,
    10%,
    20%,
    26%,
    28%,
    32%,
    100% {
      height: 7.2vmax;
    }
    5%,
    15%,
    22%,
    24%,
    30% {
      height: 7.05vmax;
    }
  }

  @keyframes ear-l {
    0%,
    10%,
    20%,
    26%,
    28%,
    82%,
    100% {
      transform: rotateZ(-50deg);
    }
    5%,
    15%,
    22%,
    24% {
      transform: rotateZ(-48deg);
    }
    30%,
    31% {
      transform: rotateZ(-30deg);
    }
    32%,
    80% {
      transform: rotateZ(-60deg);
    }
  }

  @keyframes ear-r {
    0%,
    10%,
    20%,
    26%,
    28% {
      transform: rotateZ(20deg);
    }
    5%,
    15%,
    22%,
    24% {
      transform: rotateZ(18deg);
    }
    30%,
    31% {
      transform: rotateZ(10deg);
    }
    32% {
      transform: rotateZ(25deg);
    }
  }

  @keyframes snout {
    0%,
    10%,
    20%,
    26%,
    28%,
    82%,
    100% {
      height: 3.75vmax;
    }
    5%,
    15%,
    22%,
    24% {
      height: 3.45vmax;
    }
  }

  @keyframes snout-b {
    0%,
    10%,
    20%,
    26%,
    28%,
    98%,
    100% {
      width: 1.875vmax;
    }
    5%,
    15%,
    22%,
    24% {
      width: 1.8vmax;
    }
    34%,
    98% {
      width: 1.275vmax;
    }
  }

  @keyframes shadow {
    0%,
    10%,
    20%,
    26%,
    28%,
    30%,
    84%,
    100% {
      width: 99%;
    }
    5%,
    15%,
    22%,
    24% {
      width: 101%;
    }
    34%,
    81% {
      width: 96%;
    }
  }

  @keyframes eye {
    0%,
    30% {
      width: 0.675vmax;
      height: 0.3vmax;
    }
    32%,
    59%,
    90%,
    100% {
      width: 0.525vmax;
      height: 0.525vmax;
      transform: translateY(0);
    }
    60%,
    75% {
      transform: translateY(-0.3vmax);
    }
    80%,
    85% {
      transform: translateY(0.15vmax);
    }
      .laptop-wrapper,
.dog-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}
  }`;
  

export default Animation1;

// import React from 'react';
// import styled from 'styled-components';

// const Loader = () => {
//   return (
//     <StyledWrapper>
//       <div className="main">
//         <div className="dog">
//           <div className="dog__paws">
//             <div className="dog__bl-leg leg">
//               <div className="dog__bl-paw paw" />
//               <div className="dog__bl-top top" />
//             </div>
//             <div className="dog__fl-leg leg">
//               <div className="dog__fl-paw paw" />
//               <div className="dog__fl-top top" />
//             </div>
//             <div className="dog__fr-leg leg">
//               <div className="dog__fr-paw paw" />
//               <div className="dog__fr-top top" />
//             </div>
//           </div>
//           <div className="dog__body">
//             <div className="dog__tail" />
//           </div>
//           <div className="dog__head">
//             <div className="dog__snout">
//               <div className="dog__nose" />
//               <div className="dog__eyes">
//                 <div className="dog__eye-l" />
//                 <div className="dog__eye-r" />
//               </div>
//             </div>
//           </div>
//           <div className="dog__head-c">
//             <div className="dog__ear-l" />
//             <div className="dog__ear-r" />
//           </div>
//         </div>
//       </div>
//     </StyledWrapper>
//   );
// }

// const StyledWrapper = styled.div`
//   .main {
//     position: relative;
//     width: 23.5vmax;
//     height: 23.5vmax;
//     display: flex;
//     justify-content: center;
//     align-items: center;
//   }

//   .leg {
//     position: absolute;
//     bottom: 0;
//     width: 2vmax;
//     height: 2.125vmax;
//   }

//   .paw {
//     position: absolute;
//     bottom: 0;
//     left: 0;
//     width: 1.95vmax;
//     height: 1.875vmax;
//     overflow: hidden;
//   }

//   .paw::before {
//     content: "";
//     position: absolute;
//     width: 3.75vmax;
//     height: 3.75vmax;
//     border-radius: 50%;
//   }

//   .top {
//     position: absolute;
//     bottom: 0;
//     left: 0.75vmax;
//     height: 4.5vmax;
//     width: 2.625vmax;
//     border-top-left-radius: 1.425vmax;
//     border-top-right-radius: 1.425vmax;
//     transform-origin: bottom right;
//     transform: rotateZ(90deg) translateX(-0.1vmax) translateY(1.5vmax);
//     z-index: -1;
//     background-image: linear-gradient(70deg, transparent 20%, #ff8b56 20%);
//   }

//   .dog {
//     position: relative;
//     width: 22.5vmax;
//     height: 8.25vmax;
//   }

//   .dog::before {
//     content: "";
//     position: absolute;
//     bottom: -0.75vmax;
//     right: -0.15vmax;
//     width: 100%;
//     height: 1.5vmax;
//     background-color: rgba(28, 49, 48, 0.1);
//     border-radius: 50%;
//     z-index: -1000;
//     animation: shadow 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__head {
//     position: absolute;
//     left: 4.5vmax;
//     bottom: 0;
//     width: 9.75vmax;
//     height: 8.25vmax;
//     border-top-left-radius: 4.05vmax;
//     border-top-right-radius: 4.05vmax;
//     border-bottom-right-radius: 3.3vmax;
//     border-bottom-left-radius: 3.3vmax;
//     background-color: #ff8147;
//     animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__head-c {
//     position: absolute;
//     left: 1.5vmax;
//     bottom: 0;
//     width: 9.75vmax;
//     height: 8.25vmax;
//     animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//     z-index: -1;
//   }

//   .dog__snout {
//     position: absolute;
//     left: -1.5vmax;
//     bottom: 0;
//     width: 7.5vmax;
//     height: 3.75vmax;
//     border-top-right-radius: 3vmax;
//     border-bottom-right-radius: 3vmax;
//     border-bottom-left-radius: 4.5vmax;
//     background-color: #d7dbd2;
//     animation: snout 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__snout::before {
//     content: "";
//     position: absolute;
//     left: -0.1125vmax;
//     top: -0.15vmax;
//     width: 1.875vmax;
//     height: 1.125vmax;
//     border-top-right-radius: 3vmax;
//     border-bottom-right-radius: 3vmax;
//     border-bottom-left-radius: 4.5vmax;
//     background-color: #1c3130;
//     animation: snout-b 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__nose {
//     position: absolute;
//     top: -1.95vmax;
//     left: 40%;
//     width: 0.75vmax;
//     height: 2.4vmax;
//     border-radius: 0.525vmax;
//     transform-origin: bottom;
//     transform: rotateZ(10deg);
//     background-color: #d7dbd2;
//   }

//   .dog__eye-l,
//   .dog__eye-r {
//     position: absolute;
//     top: -0.9vmax;
//     width: 0.675vmax;
//     height: 0.375vmax;
//     border-radius: 50%;
//     background-color: #1c3130;
//     animation: eye 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__eye-l {
//     left: 27%;
//   }

//   .dog__eye-r {
//     left: 65%;
//   }

//   .dog__ear-l,
//   .dog__ear-r {
//     position: absolute;
//     width: 10.5vmax;
//     height: 3.375vmax;
//     border-top-left-radius: 0vmax;
//     border-top-right-radius: 0vmax;
//     border-bottom-right-radius: 3.3vmax;
//     border-bottom-left-radius: 3.3vmax;
//     background-color: #e26538;
//   }

//   .dog__ear-l {
//     top: 1.5vmax;
//     left: 6vmax;
//     transform-origin: bottom left;
//     transform: rotateZ(-50deg);
//     z-index: -1;
//     animation: ear-l 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__ear-r {
//     top: 1.5vmax;
//     right: 3vmax;
//     transform-origin: bottom right;
//     transform: rotateZ(20deg);
//     z-index: -2;
//     animation: ear-r 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__body {
//     display: flex;
//     justify-content: center;
//     align-items: flex-end;
//     position: absolute;
//     bottom: 0.3vmax;
//     left: 3.75vmax;
//     width: 18.75vmax;
//     height: 7.2vmax;
//     border-top-left-radius: 3vmax;
//     border-top-right-radius: 6vmax;
//     border-bottom-right-radius: 1.5vmax;
//     border-bottom-left-radius: 6vmax;
//     background-color: #ff702e;
//     z-index: -2;
//     animation: body 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
//   }

//   .dog__tail {
//     position: absolute;
//     right: -3vmax;
//     height: 1.5vmax;
//     width: 4.5vmax;
//     background-color: #e96839;
//     border-radius: 1.5vmax;
//   }

//   .dog__paws {
//     position: absolute;
//     bottom: 0;
//     left: 7.5vmax;
//     width: 12vmax;
//     height: 3vmax;
//   }

//   .dog__bl-leg {
//     left: -3vmax;
//     z-index: -10;
//   }

//   .dog__bl-paw::before {
//     background-color: #bec4b6;
//   }

//   .dog__bl-top {
//     background-image: linear-gradient(80deg, transparent 20%, #e96839 20%);
//   }

//   .dog__fl-leg {
//     z-index: 10;
//     left: 0;
//   }

//   .dog__fl-paw::before {
//     background-color: #d7dbd2;
//   }

//   .dog__fr-leg {
//     right: 0;
//   }

//   .dog__fr-paw::before {
//     background-color: #d7dbd2;
//   }

//   /*==============================*/

//   @keyframes head {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     90%,
//     100% {
//       height: 8.25vmax;
//       bottom: 0;
//       transform-origin: bottom right;
//       transform: rotateZ(0);
//     }
//     5%,
//     15%,
//     22%,
//     24%,
//     30% {
//       height: 8.1vmax;
//     }
//     32%,
//     50% {
//       height: 8.25vmax;
//     }
//     55%,
//     60% {
//       bottom: 0.75vmax;
//       transform-origin: bottom right;
//       transform: rotateZ(0);
//     }
//     70%,
//     80% {
//       bottom: 0.75vmax;
//       transform-origin: bottom right;
//       transform: rotateZ(10deg);
//     }
//   }

//   @keyframes body {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     32%,
//     100% {
//       height: 7.2vmax;
//     }
//     5%,
//     15%,
//     22%,
//     24%,
//     30% {
//       height: 7.05vmax;
//     }
//   }

//   @keyframes ear-l {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     82%,
//     100% {
//       transform: rotateZ(-50deg);
//     }
//     5%,
//     15%,
//     22%,
//     24% {
//       transform: rotateZ(-48deg);
//     }
//     30%,
//     31% {
//       transform: rotateZ(-30deg);
//     }
//     32%,
//     80% {
//       transform: rotateZ(-60deg);
//     }
//   }

//   @keyframes ear-r {
//     0%,
//     10%,
//     20%,
//     26%,
//     28% {
//       transform: rotateZ(20deg);
//     }
//     5%,
//     15%,
//     22%,
//     24% {
//       transform: rotateZ(18deg);
//     }
//     30%,
//     31% {
//       transform: rotateZ(10deg);
//     }
//     32% {
//       transform: rotateZ(25deg);
//     }
//   }

//   @keyframes snout {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     82%,
//     100% {
//       height: 3.75vmax;
//     }
//     5%,
//     15%,
//     22%,
//     24% {
//       height: 3.45vmax;
//     }
//   }

//   @keyframes snout-b {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     98%,
//     100% {
//       width: 1.875vmax;
//     }
//     5%,
//     15%,
//     22%,
//     24% {
//       width: 1.8vmax;
//     }
//     34%,
//     98% {
//       width: 1.275vmax;
//     }
//   }

//   @keyframes shadow {
//     0%,
//     10%,
//     20%,
//     26%,
//     28%,
//     30%,
//     84%,
//     100% {
//       width: 99%;
//     }
//     5%,
//     15%,
//     22%,
//     24% {
//       width: 101%;
//     }
//     34%,
//     81% {
//       width: 96%;
//     }
//   }

//   @keyframes eye {
//     0%,
//     30% {
//       width: 0.675vmax;
//       height: 0.3vmax;
//     }
//     32%,
//     59%,
//     90%,
//     100% {
//       width: 0.525vmax;
//       height: 0.525vmax;
//       transform: translateY(0);
//     }
//     60%,
//     75% {
//       transform: translateY(-0.3vmax);
//     }
//     80%,
//     85% {
//       transform: translateY(0.15vmax);
//     }
//   }`;

// export default Loader;

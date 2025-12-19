import React from "react";
import styled from "styled-components";
import { slide1,slide2,slide3,slide4,slide5,slide6,slide7 } from "@/assets";
const slides = [
  slide1,slide2,slide3,slide4,slide5,slide6,slide7
];

const VerticalCarousel = () => {
  const quantity = slides.length;
  
  return (
    <StyledWrapper style={{ '--height': '100%', '--quantity': quantity } as React.CSSProperties}>
      <div className="slider">
        <div className="list">
          {slides.map((src, index) => (
            <div
              key={index}
              className="item"
              style={{ '--position': index + 1 } as React.CSSProperties}
            >
              {/* Bootstrap-like carousel-item */}
              <div className="carousel-item">
                <img src={src} alt={`Slide ${index + 1}`} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  width: 100%;
  height: 100%;
  min-height: 300px;

  .slider {
    width: 100%;
    height: 100%;
    min-height: 300px;
    overflow: hidden;
    position: relative;
    border-radius:10px;
    /* 👇 control spacing here */
    --gap: 950px;
  }

  .list {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 300px;
  }

  .item {
    width: 100%;
    height: 100%;
    min-height: 300px;
    position: absolute;
    top: 100%;

    animation: verticalRun 50s linear infinite;
    animation-delay: calc(
      (50s / var(--quantity)) * (var(--position) - 1) - 50s
    );
  }

  /* ✅ spacing is handled here */
  @keyframes verticalRun {
    from {
      top: calc(100% + var(--gap));
    }
    to {
      top: calc(-100% - var(--gap));
    }
  }

  .carousel-item {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
  }

  .carousel-item img {
    width: 100%;
    height: 100%;
    min-height: 200px;
    object-fit: cover;
    border-radius: 20px;
    display: block;
  }
`;



export default VerticalCarousel;
